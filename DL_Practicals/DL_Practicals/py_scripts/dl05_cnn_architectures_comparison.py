# %% [markdown]
# # Practical 5: Comparative Study of CNN Architectures for Image Classification
# **Aim:** Implement the main CNN architecture families on the same dataset and compare them fairly
# (same data, optimizer, epochs and augmentation) on accuracy, parameters, computation (MACs), training time,
# inference time, loss curves and overfitting.
#
# | Family | Key idea |
# |---|---|
# | Basic CNN | Conv + pooling stack, the baseline |
# | LeNet-5 | First CNN: small kernels, average pooling, tanh |
# | AlexNet-style | Deeper, ReLU, dropout |
# | VGG-style | Stacks of 3x3 convolutions, batch normalization |
# | ResNet-style | Residual (skip) connections |
# | Inception-style | Parallel 1x1 / 3x3 / 5x5 branches (multi-scale features) |
# | MobileNet-style | Depthwise-separable convolutions (very few parameters) |
#
# Compact versions are used so all seven train in reasonable time on a laptop (CIFAR-10 subset; change
# `N_TRAIN` / `EPOCHS` for the full run).

# %%
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import confusion_matrix

SEED = 42
tf.keras.utils.set_random_seed(SEED)
N_TRAIN, N_TEST = 20000, 5000
EPOCHS = 10
BATCH = 64
CLASSES = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]

# %% [markdown]
# ## 1. Load and preprocess CIFAR-10

# %%
(x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
x_train, y_train = x_train[:N_TRAIN].astype("float32"), y_train[:N_TRAIN].ravel()
x_test, y_test = x_test[:N_TEST].astype("float32"), y_test[:N_TEST].ravel()
print("Train:", x_train.shape, "Test:", x_test.shape)

plt.figure(figsize=(10, 2))
for i in range(10):
    plt.subplot(1, 10, i + 1); plt.imshow(x_train[i].astype("uint8")); plt.title(CLASSES[y_train[i]], fontsize=8); plt.axis("off")
plt.show()

# %% [markdown]
# ## 2. The seven architectures
# Every model starts with the same preprocessing (rescale + random horizontal flip) and ends with a 10-way softmax.

# %%
def stem(name):
    inp = layers.Input((32, 32, 3))
    x = layers.Rescaling(1 / 255.0)(inp)
    x = layers.RandomFlip("horizontal")(x)           # augmentation, active only during training
    return inp, x

def head(inp, x, name):
    return keras.Model(inp, layers.Dense(10, activation="softmax")(x), name=name)

def basic_cnn():
    inp, x = stem("basic")
    x = layers.Conv2D(32, 3, padding="same", activation="relu")(x); x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(64, 3, padding="same", activation="relu")(x); x = layers.MaxPooling2D()(x)
    x = layers.Flatten()(x); x = layers.Dense(128, activation="relu")(x)
    return head(inp, x, "Basic CNN")

def lenet5():
    inp, x = stem("lenet")
    x = layers.Conv2D(6, 5, activation="tanh")(x); x = layers.AveragePooling2D()(x)
    x = layers.Conv2D(16, 5, activation="tanh")(x); x = layers.AveragePooling2D()(x)
    x = layers.Flatten()(x)
    x = layers.Dense(120, activation="tanh")(x); x = layers.Dense(84, activation="tanh")(x)
    return head(inp, x, "LeNet-5")

def alexnet_style():
    inp, x = stem("alex")
    x = layers.Conv2D(64, 3, padding="same", activation="relu")(x); x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(128, 3, padding="same", activation="relu")(x); x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(192, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(192, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(128, 3, padding="same", activation="relu")(x); x = layers.MaxPooling2D()(x)
    x = layers.Flatten()(x)
    x = layers.Dense(512, activation="relu")(x); x = layers.Dropout(0.5)(x)
    x = layers.Dense(512, activation="relu")(x); x = layers.Dropout(0.5)(x)
    return head(inp, x, "AlexNet-style")

def vgg_style():
    inp, x = stem("vgg")
    for filters in (32, 64, 128):
        for _ in range(2):                            # two 3x3 convs per block, as in VGG
            x = layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
            x = layers.BatchNormalization()(x); x = layers.ReLU()(x)
        x = layers.MaxPooling2D()(x)
    x = layers.Flatten()(x); x = layers.Dense(256, activation="relu")(x); x = layers.Dropout(0.4)(x)
    return head(inp, x, "VGG-style")

def res_block(x, filters, stride=1):
    shortcut = x
    y = layers.Conv2D(filters, 3, strides=stride, padding="same", use_bias=False)(x)
    y = layers.BatchNormalization()(y); y = layers.ReLU()(y)
    y = layers.Conv2D(filters, 3, padding="same", use_bias=False)(y)
    y = layers.BatchNormalization()(y)
    if stride != 1 or shortcut.shape[-1] != filters:  # match shape with a 1x1 projection
        shortcut = layers.Conv2D(filters, 1, strides=stride, use_bias=False)(shortcut)
        shortcut = layers.BatchNormalization()(shortcut)
    return layers.ReLU()(layers.Add()([y, shortcut]))   # <- skip connection

def resnet_style():
    inp, x = stem("res")
    x = layers.Conv2D(32, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x); x = layers.ReLU()(x)
    x = res_block(x, 32); x = res_block(x, 64, stride=2); x = res_block(x, 128, stride=2)
    x = layers.GlobalAveragePooling2D()(x)
    return head(inp, x, "ResNet-style")

def inception_block(x, f1, f3, f5, fp):
    b1 = layers.Conv2D(f1, 1, padding="same", activation="relu")(x)
    b2 = layers.Conv2D(f3, 1, padding="same", activation="relu")(x)
    b2 = layers.Conv2D(f3, 3, padding="same", activation="relu")(b2)
    b3 = layers.Conv2D(f5, 1, padding="same", activation="relu")(x)
    b3 = layers.Conv2D(f5, 5, padding="same", activation="relu")(b3)
    b4 = layers.MaxPooling2D(3, strides=1, padding="same")(x)
    b4 = layers.Conv2D(fp, 1, padding="same", activation="relu")(b4)
    return layers.Concatenate()([b1, b2, b3, b4])    # parallel multi-scale branches

def inception_style():
    inp, x = stem("inc")
    x = layers.Conv2D(32, 3, padding="same", activation="relu")(x); x = layers.MaxPooling2D()(x)
    x = inception_block(x, 16, 24, 8, 8); x = layers.MaxPooling2D()(x)
    x = inception_block(x, 32, 48, 16, 16); x = layers.MaxPooling2D()(x)
    x = layers.GlobalAveragePooling2D()(x)
    return head(inp, x, "Inception-style")

def ds_block(x, filters, stride=1):
    x = layers.DepthwiseConv2D(3, strides=stride, padding="same", use_bias=False)(x)   # spatial filtering per channel
    x = layers.BatchNormalization()(x); x = layers.ReLU()(x)
    x = layers.Conv2D(filters, 1, use_bias=False)(x)                                   # 1x1 channel mixing
    x = layers.BatchNormalization()(x)
    return layers.ReLU()(x)

def mobilenet_style():
    inp, x = stem("mob")
    x = layers.Conv2D(32, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x); x = layers.ReLU()(x)
    for f, s in [(64, 1), (128, 2), (128, 1), (256, 2), (256, 1)]:
        x = ds_block(x, f, s)
    x = layers.GlobalAveragePooling2D()(x)
    return head(inp, x, "MobileNet-style")

builders = [basic_cnn, lenet5, alexnet_style, vgg_style, resnet_style, inception_style, mobilenet_style]

# %% [markdown]
# ## 3. Computational cost: multiply-accumulate operations (MACs) per image
# Counted from layer shapes: conv = out_h x out_w x k x k x c_in x c_out, depthwise conv = out_h x out_w x k x k x c_in,
# dense = inputs x outputs.

# %%
def count_macs(model):
    total = 0
    for layer in model.layers:
        out = layer.output.shape
        if isinstance(layer, layers.DepthwiseConv2D):
            kh, kw, cin, mult = layer.kernel.shape
            total += out[1] * out[2] * kh * kw * cin * mult
        elif isinstance(layer, layers.Conv2D):
            kh, kw, cin, cout = layer.kernel.shape
            total += out[1] * out[2] * kh * kw * cin * cout
        elif isinstance(layer, layers.Dense):
            total += int(layer.kernel.shape[0]) * int(layer.kernel.shape[1])
    return total

for b in builders:
    m = b()
    print(f"{m.name:16s} params = {m.count_params():>9,d}   MACs = {count_macs(m) / 1e6:8.2f} M")

# %% [markdown]
# ## 4. Train and evaluate all models under identical conditions

# %%
rows, histories, test_preds = [], {}, {}
for build in builders:
    tf.keras.utils.set_random_seed(SEED)
    model = build()
    model.compile(optimizer=keras.optimizers.Adam(1e-3),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    t0 = time.time()
    h = model.fit(x_train, y_train, epochs=EPOCHS, batch_size=BATCH, validation_split=0.1, verbose=0)
    train_time = time.time() - t0

    t0 = time.time()
    probs = model.predict(x_test, verbose=0)
    infer_ms = 1000 * (time.time() - t0) / len(x_test)

    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    gap = h.history["accuracy"][-1] - h.history["val_accuracy"][-1]
    histories[model.name] = h.history
    test_preds[model.name] = probs.argmax(axis=1)
    rows.append([model.name, model.count_params(), count_macs(model) / 1e6, h.history["loss"][-1],
                 test_loss, test_acc, gap, train_time, infer_ms])
    print(f"{model.name:16s} test acc = {test_acc:.4f} | train time = {train_time:.0f}s")

results = pd.DataFrame(rows, columns=["Model", "Parameters", "MACs (M)", "Final train loss", "Test loss",
                                      "Test accuracy", "Train-val gap", "Train time (s)", "Inference (ms/img)"])
display(results.sort_values("Test accuracy", ascending=False).round(4))

# %% [markdown]
# ## 5. Loss curves and validation accuracy

# %%
fig, ax = plt.subplots(1, 3, figsize=(20, 4.8))
for name, h in histories.items():
    ax[0].plot(h["loss"], label=name)
    ax[1].plot(h["val_loss"], label=name)
    ax[2].plot(h["val_accuracy"], label=name)
for a, t in zip(ax, ["Training loss", "Validation loss", "Validation accuracy"]):
    a.set_title(t); a.set_xlabel("Epoch"); a.grid(True)
ax[2].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6. Accuracy versus cost (the trade-off)
# Left: accuracy against parameters (bubble size = MACs). Right: accuracy, training time and overfitting gap.

# %%
fig, ax = plt.subplots(1, 2, figsize=(16, 5.5))
ax[0].scatter(results["Parameters"] / 1e6, results["Test accuracy"], s=results["MACs (M)"] * 6 + 40, alpha=0.6)
for _, r in results.iterrows():
    ax[0].annotate(r["Model"], (r["Parameters"] / 1e6, r["Test accuracy"]), fontsize=9, xytext=(5, 5), textcoords="offset points")
ax[0].set_xscale("log"); ax[0].set_xlabel("Parameters (millions, log scale)"); ax[0].set_ylabel("Test accuracy")
ax[0].set_title("Accuracy vs model size (bubble = MACs)"); ax[0].grid(True, which="both", alpha=0.3)

order = results.sort_values("Test accuracy")
ax[1].barh(order["Model"], order["Test accuracy"], color="tab:blue", label="Test accuracy")
ax[1].set_xlim(order["Test accuracy"].min() - 0.05, 1.0)
for i, (_, r) in enumerate(order.iterrows()):
    ax[1].text(r["Test accuracy"] + 0.003, i, f"{r['Train time (s)']:.0f}s | gap {r['Train-val gap']:+.2f}", va="center", fontsize=8)
ax[1].set_title("Test accuracy  (labels: train time | train-val gap)")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 7. Per-class accuracy and confusion matrix of the best model

# %%
per_class = pd.DataFrame({name: [(pred[y_test == c] == c).mean() for c in range(10)]
                          for name, pred in test_preds.items()}, index=CLASSES)
plt.figure(figsize=(10, 5))
plt.imshow(per_class.values, cmap="viridis", aspect="auto")
plt.xticks(range(len(per_class.columns)), per_class.columns, rotation=30, ha="right")
plt.yticks(range(10), CLASSES); plt.colorbar(label="accuracy")
plt.title("Per-class test accuracy"); plt.tight_layout(); plt.show()

best = results.loc[results["Test accuracy"].idxmax(), "Model"]
cm = confusion_matrix(y_test, test_preds[best])
plt.figure(figsize=(7, 6)); plt.imshow(cm, cmap="Blues")
plt.xticks(range(10), CLASSES, rotation=60, ha="right"); plt.yticks(range(10), CLASSES)
plt.title(f"Confusion matrix - {best}"); plt.colorbar(); plt.tight_layout(); plt.show()

# %% [markdown]
# ## 8. Conclusion
# * **Basic CNN / LeNet-5:** cheapest and fastest but lowest accuracy; LeNet's tanh + average pooling limits learning on colour images.
# * **AlexNet-style:** more depth and dropout raise accuracy, but most parameters sit in the dense layers.
# * **VGG-style:** stacked 3x3 convolutions with batch normalization are accurate but computationally heavy (many MACs).
# * **ResNet-style:** skip connections ease gradient flow, so it trains fast and reaches high accuracy with few parameters.
# * **Inception-style:** parallel 1x1/3x3/5x5 branches capture multi-scale features efficiently (1x1 convolutions reduce cost).
# * **MobileNet-style:** depthwise-separable convolutions give the fewest parameters and MACs, a small accuracy
#   trade-off in return - best for mobile/edge devices.
# * Overall: accuracy rises with depth and smarter blocks (residual, inception, normalization), but cost rises too;
#   the best choice depends on the accuracy-versus-resources requirement (see the trade-off plot).
