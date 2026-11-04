# %% [markdown]
# # Practical 7: Comparative Study of LeNet, AlexNet, VGG16 and ResNet50 (CIFAR-10) - CO1, CO2, CO3
# **Aim:** Implement and compare four CNN architectures, apply transfer learning with pre-trained ResNet50
# (feature extraction and fine-tuning), and analyse overfitting and vanishing gradients.
#
# *Note:* To keep run time reasonable on a laptop, a subset of CIFAR-10 is used (change `N_TRAIN`/`N_TEST`
# for the full dataset). Pre-trained weights are downloaded once from the internet.

# %%
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

SEED = 42
tf.keras.utils.set_random_seed(SEED)
N_TRAIN, N_TEST = 10000, 2000
EPOCHS = 5
BATCH = 64

# %% [markdown]
# ## 1. Data

# %%
(x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
x_train, y_train = x_train[:N_TRAIN].astype("float32"), y_train[:N_TRAIN].ravel()
x_test, y_test = x_test[:N_TEST].astype("float32"), y_test[:N_TEST].ravel()
print(x_train.shape, x_test.shape)

# %% [markdown]
# ## 2. Architectures (adapted to 32x32 inputs)

# %%
def lenet():
    return keras.Sequential([
        layers.Input((32, 32, 3)), layers.Rescaling(1 / 255.0),
        layers.Conv2D(6, 5, activation="tanh"), layers.AveragePooling2D(),
        layers.Conv2D(16, 5, activation="tanh"), layers.AveragePooling2D(),
        layers.Flatten(),
        layers.Dense(120, activation="tanh"), layers.Dense(84, activation="tanh"),
        layers.Dense(10, activation="softmax")], name="LeNet")

def alexnet():
    return keras.Sequential([
        layers.Input((32, 32, 3)), layers.Rescaling(1 / 255.0),
        layers.Conv2D(96, 3, padding="same", activation="relu"), layers.MaxPooling2D(2),
        layers.Conv2D(256, 3, padding="same", activation="relu"), layers.MaxPooling2D(2),
        layers.Conv2D(384, 3, padding="same", activation="relu"),
        layers.Conv2D(384, 3, padding="same", activation="relu"),
        layers.Conv2D(256, 3, padding="same", activation="relu"), layers.MaxPooling2D(2),
        layers.Flatten(),
        layers.Dense(1024, activation="relu"), layers.Dropout(0.5),
        layers.Dense(1024, activation="relu"), layers.Dropout(0.5),
        layers.Dense(10, activation="softmax")], name="AlexNet")

def vgg16_scratch():
    base = keras.applications.VGG16(include_top=False, weights=None, input_shape=(32, 32, 3))
    return keras.Sequential([
        layers.Input((32, 32, 3)), layers.Rescaling(1 / 255.0), base,
        layers.Flatten(), layers.Dense(256, activation="relu"), layers.Dropout(0.5),
        layers.Dense(10, activation="softmax")], name="VGG16")

def resnet50_scratch():
    base = keras.applications.ResNet50(include_top=False, weights=None, input_shape=(32, 32, 3))
    return keras.Sequential([
        layers.Input((32, 32, 3)), layers.Rescaling(1 / 255.0), base,
        layers.GlobalAveragePooling2D(), layers.Dense(10, activation="softmax")], name="ResNet50")

# %% [markdown]
# ## 3. Train and evaluate helper

# %%
results, histories = [], {}

def train_eval(model, name, epochs=EPOCHS, lr=1e-3, x_tr=None, x_te=None):
    x_tr = x_train if x_tr is None else x_tr
    x_te = x_test if x_te is None else x_te
    model.compile(optimizer=keras.optimizers.Adam(lr),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    t0 = time.time()
    h = model.fit(x_tr, y_train, epochs=epochs, batch_size=BATCH, validation_split=0.1, verbose=0)
    elapsed = time.time() - t0
    test_loss, test_acc = model.evaluate(x_te, y_test, verbose=0)
    gap = h.history["accuracy"][-1] - h.history["val_accuracy"][-1]
    histories[name] = h.history
    results.append([name, model.count_params(), h.history["loss"][-1], test_acc, gap, elapsed])
    print(f"{name:34s} test acc = {test_acc:.4f} | time = {elapsed:.0f}s")

# %% [markdown]
# ## 4. Train the four architectures from scratch

# %%
for build in (lenet, alexnet, vgg16_scratch, resnet50_scratch):
    tf.keras.utils.set_random_seed(SEED)
    m = build()
    train_eval(m, m.name + " (scratch)")

# %% [markdown]
# ## 5. Transfer learning with pre-trained ResNet50 (ImageNet weights)
# Images are resized to 64x64 (ResNet50 works better with larger inputs than 32x32).
# **(a) Feature extraction:** the base is frozen and only the new classifier head is trained.
# **(b) Fine-tuning:** the last ~30 layers of the base are unfrozen and trained with a small learning rate.

# %%
SIZE = 64
x_train_r = tf.image.resize(x_train, (SIZE, SIZE)).numpy()
x_test_r = tf.image.resize(x_test, (SIZE, SIZE)).numpy()

def resnet_tl(fine_tune_layers=0):
    base = keras.applications.ResNet50(include_top=False, weights="imagenet", input_shape=(SIZE, SIZE, 3))
    base.trainable = False
    if fine_tune_layers:
        base.trainable = True
        for layer in base.layers[:-fine_tune_layers]:
            layer.trainable = False
        for layer in base.layers:                       # keep BatchNorm statistics frozen
            if isinstance(layer, layers.BatchNormalization):
                layer.trainable = False
    inp = layers.Input((SIZE, SIZE, 3))
    x = keras.applications.resnet50.preprocess_input(inp)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(10, activation="softmax")(x)
    return keras.Model(inp, out, name="ResNet50_TL")

tf.keras.utils.set_random_seed(SEED)
train_eval(resnet_tl(0), "ResNet50 feature extraction", lr=1e-3, x_tr=x_train_r, x_te=x_test_r)
tf.keras.utils.set_random_seed(SEED)
train_eval(resnet_tl(30), "ResNet50 fine-tuning (last 30)", lr=1e-4, x_tr=x_train_r, x_te=x_test_r)

# %% [markdown]
# ## 6. Comparison table and curves

# %%
table = pd.DataFrame(results, columns=["Model", "Parameters", "Final train loss", "Test accuracy",
                                       "Train-val acc gap (overfitting)", "Training time (s)"])
display(table.round(4))

fig, ax = plt.subplots(1, 3, figsize=(20, 4.8))
for name, h in histories.items():
    ax[0].plot(h["loss"], label=name)
    ax[1].plot(h["val_accuracy"], label=name)
ax[0].set_title("Training loss"); ax[1].set_title("Validation accuracy")
for a in ax[:2]: a.set_xlabel("Epoch"); a.grid(True)
ax[1].legend(fontsize=7)
ax[2].barh(table["Model"], table["Test accuracy"]); ax[2].set_title("Test accuracy")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 7. Vanishing-gradient analysis
# Compare the gradient norm of the **first** conv layer with that of the **last** conv layer in the plain
# deep VGG16 versus ResNet50 (skip connections) at initialization.

# %%
def first_last_grad(model_fn, size=32):
    tf.keras.utils.set_random_seed(SEED)
    model = model_fn()
    base = [l for l in model.layers if isinstance(l, keras.Model)][0]
    convs = [l for l in base.layers if isinstance(l, layers.Conv2D)]
    xb, yb = x_train[:128], y_train[:128]
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(keras.losses.sparse_categorical_crossentropy(yb, model(xb, training=True)))
    g = tape.gradient(loss, [convs[0].kernel, convs[-1].kernel])
    return float(tf.norm(g[0])), float(tf.norm(g[1]))

rows = []
for fn, name in [(vgg16_scratch, "VGG16 (plain)"), (resnet50_scratch, "ResNet50 (skip connections)")]:
    f, l = first_last_grad(fn)
    rows.append([name, f, l, f / l])
display(pd.DataFrame(rows, columns=["Model", "||grad|| first conv", "||grad|| last conv", "ratio first/last"]))

# %% [markdown]
# ## 8. Conclusion
# * **LeNet** is tiny and fast but has limited capacity; **AlexNet** adds ReLU, dropout and more depth.
# * **VGG16** is deep and plain: many parameters, slow, and hard to train from scratch (vanishing gradients) in few epochs.
# * **ResNet50** uses skip connections, so gradients flow to early layers more easily (ratio first/last is closer to 1).
# * **Transfer learning** gives the best accuracy with the least training: pre-trained features generalize,
#   and fine-tuning the last layers adapts them to CIFAR-10 further.
# * Models trained from scratch on small data show a larger train-validation gap (overfitting); dropout and pre-training reduce it.
