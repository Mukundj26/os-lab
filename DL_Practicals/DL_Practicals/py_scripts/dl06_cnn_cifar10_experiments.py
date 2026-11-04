# %% [markdown]
# # Practical 6: Implementation and Performance Analysis of CNN (CIFAR-10) - CO1, CO2, CO3
# **Aim:** Build a basic CNN, experiment with kernel size, stride, padding and pooling, and visualize
# convolutional filters and feature maps.

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
EPOCHS = 5
CLASSES = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]

# %% [markdown]
# ## 1. Load and preprocess CIFAR-10

# %%
(x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
y_train, y_test = y_train.ravel(), y_test.ravel()
print(x_train.shape, x_test.shape)

plt.figure(figsize=(10, 2))
for i in range(10):
    plt.subplot(1, 10, i + 1); plt.imshow(x_train[i]); plt.title(CLASSES[y_train[i]], fontsize=8); plt.axis("off")
plt.show()

# %% [markdown]
# ## 2. Configurable CNN

# %%
def build_cnn(kernel=3, stride=1, padding="same", pooling="max"):
    Pool = layers.MaxPooling2D if pooling == "max" else layers.AveragePooling2D
    model = keras.Sequential([
        layers.Input(shape=(32, 32, 3)),
        layers.Conv2D(32, kernel, strides=stride, padding=padding, activation="relu", name="conv1"),
        Pool(2),
        layers.Conv2D(64, kernel, strides=1, padding=padding, activation="relu", name="conv2"),
        Pool(2),
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model

# baseline
base = build_cnn()
base.summary()

# %% [markdown]
# ## 3. Experiments: kernel size, stride, padding, pooling
# One factor is changed at a time from the baseline (3x3, stride 1, same padding, max pooling).

# %%
configs = {
    "Baseline (3x3, s1, same, max)": dict(),
    "Kernel 5x5":                    dict(kernel=5),
    "Stride 2":                      dict(stride=2),
    "Padding valid":                 dict(padding="valid"),
    "Average pooling":               dict(pooling="avg"),
}
rows, hist, models = [], {}, {}
for name, kw in configs.items():
    tf.keras.utils.set_random_seed(SEED)
    m = build_cnn(**kw)
    t0 = time.time()
    h = m.fit(x_train, y_train, epochs=EPOCHS, batch_size=128, validation_split=0.1, verbose=0)
    elapsed = time.time() - t0
    loss, acc = m.evaluate(x_test, y_test, verbose=0)
    hist[name], models[name] = h.history, m
    rows.append([name, m.count_params(), h.history["loss"][-1], loss, acc, elapsed])
    print(f"{name:32s} test acc = {acc:.4f}")

results = pd.DataFrame(rows, columns=["Configuration", "Parameters", "Final train loss", "Test loss", "Test accuracy", "Time (s)"])
display(results.round(4))

# %%
fig, ax = plt.subplots(1, 2, figsize=(15, 4.5))
for name, h in hist.items():
    ax[0].plot(h["loss"], marker="o", label=name)
ax[0].set_title("Training loss"); ax[0].set_xlabel("Epoch"); ax[0].legend(fontsize=8); ax[0].grid(True)
ax[1].barh(results["Configuration"], results["Test accuracy"])
ax[1].set_title("Test accuracy"); ax[1].set_xlim(results["Test accuracy"].min() - 0.05, results["Test accuracy"].max() + 0.02)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 4. Visualize learned convolution filters (first layer of the baseline)

# %%
model = models["Baseline (3x3, s1, same, max)"]
filters, biases = model.get_layer("conv1").get_weights()
f_min, f_max = filters.min(), filters.max()
filters = (filters - f_min) / (f_max - f_min)                # scale to 0-1 for display
n = filters.shape[-1]
plt.figure(figsize=(12, 3))
for i in range(n):
    plt.subplot(4, 8, i + 1); plt.imshow(filters[:, :, :, i]); plt.axis("off")
plt.suptitle("Learned 3x3 filters of conv1 (32 filters)"); plt.show()

# %% [markdown]
# ## 5. Visualize feature maps for one test image

# %%
img = x_test[0:1]
plt.figure(figsize=(3, 3)); plt.imshow(img[0]); plt.title(f"Input: {CLASSES[y_test[0]]}"); plt.axis("off"); plt.show()

feature_model = keras.Model(model.inputs, [model.get_layer("conv1").output, model.get_layer("conv2").output])
fmaps = feature_model.predict(img, verbose=0)
for layer_name, fm in zip(["conv1", "conv2"], fmaps):
    maps = fm[0]
    cols = 8
    plt.figure(figsize=(14, 2 * (min(maps.shape[-1], 32) // cols)))
    for i in range(min(maps.shape[-1], 32)):
        plt.subplot(min(maps.shape[-1], 32) // cols, cols, i + 1)
        plt.imshow(maps[:, :, i], cmap="viridis"); plt.axis("off")
    plt.suptitle(f"Feature maps - {layer_name} (first 32 channels)"); plt.show()

# %% [markdown]
# ## 6. Conclusion
# * **Kernel size:** 5x5 sees a larger receptive field but has more parameters and computation than 3x3.
# * **Stride 2:** down-samples early, reducing computation and parameters but losing fine detail (usually lower accuracy).
# * **Padding:** `same` keeps spatial size and border information; `valid` shrinks the maps and loses edge pixels.
# * **Pooling:** max pooling keeps the strongest activation (sharp features) and normally beats average pooling, which smooths.
# * Early filters learn edges/colour blobs; deeper feature maps are more abstract and less visually interpretable.
