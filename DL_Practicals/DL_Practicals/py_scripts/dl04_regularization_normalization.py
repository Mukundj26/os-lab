# %% [markdown]
# # Practical 4: Regularization and Normalization Techniques (Fashion-MNIST) - CO1, CO2
# **Aim:** Compare Dropout (p=0.5), L1/L2 regularization, early stopping (patience=5), data augmentation
# (random rotation + horizontal flip), and Batch vs Layer Normalization on a deep MLP.

# %%
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers

SEED = 42
tf.keras.utils.set_random_seed(SEED)
EPOCHS = 30            # early stopping may end training sooner

# %% [markdown]
# ## 1. Load and split data

# %%
(x_full, y_full), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()
x_full = (x_full.astype("float32") / 255.0)[..., None]       # add channel axis for augmentation layers
x_test = (x_test.astype("float32") / 255.0)[..., None]
x_train, y_train = x_full[:10000], y_full[:10000]            # smaller train set makes overfitting visible
x_val, y_val = x_full[50000:], y_full[50000:]
print(x_train.shape, x_val.shape, x_test.shape)

# %% [markdown]
# ## 2. Model builder
# Each option is switched on/off through arguments, so every technique is compared against the same baseline.

# %%
def build(dropout=0.0, reg=None, norm=None, augment=False, depth=4, units=256):
    inp = layers.Input(shape=(28, 28, 1))
    x = inp
    if augment:                                   # active only during training
        x = layers.RandomRotation(0.1)(x)         # up to +/- 10% of a full turn (36 degrees)
        x = layers.RandomFlip("horizontal")(x)
    x = layers.Flatten()(x)
    for _ in range(depth):
        x = layers.Dense(units, kernel_regularizer=reg)(x)
        if norm == "batch":
            x = layers.BatchNormalization()(x)
        elif norm == "layer":
            x = layers.LayerNormalization()(x)
        x = layers.Activation("relu")(x)
        if dropout > 0:
            x = layers.Dropout(dropout)(x)
    out = layers.Dense(10, activation="softmax")(x)
    m = keras.Model(inp, out)
    m.compile(optimizer=keras.optimizers.Adam(0.001),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return m

early_stop = lambda: keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

experiments = {
    "Baseline (no regularization)":  dict(kw={},                                  es=False),
    "Dropout (p=0.5)":               dict(kw=dict(dropout=0.5),                   es=False),
    "L1 (1e-5)":                     dict(kw=dict(reg=regularizers.l1(1e-5)),     es=False),
    "L2 (1e-4)":                     dict(kw=dict(reg=regularizers.l2(1e-4)),     es=False),
    "Early stopping (patience=5)":   dict(kw={},                                  es=True),
    "Data augmentation":             dict(kw=dict(augment=True),                  es=False),
    "Batch Normalization":           dict(kw=dict(norm="batch"),                  es=False),
    "Layer Normalization":           dict(kw=dict(norm="layer"),                  es=False),
}

# %% [markdown]
# ## 3. Train all configurations

# %%
hist, rows = {}, []
for name, cfg in experiments.items():
    tf.keras.utils.set_random_seed(SEED)
    model = build(**cfg["kw"])
    cbs = [early_stop()] if cfg["es"] else []
    t0 = time.time()
    h = model.fit(x_train, y_train, validation_data=(x_val, y_val),
                  epochs=EPOCHS, batch_size=128, callbacks=cbs, verbose=0)
    elapsed = time.time() - t0
    hist[name] = h.history
    val_acc = np.array(h.history["val_accuracy"])
    epochs_run = len(val_acc)
    conv = int(np.argmax(val_acc >= 0.95 * val_acc.max())) + 1       # epoch to reach 95% of best val acc
    test_acc = model.evaluate(x_test, y_test, verbose=0)[1]
    gap = h.history["accuracy"][-1] - val_acc[-1]                      # generalization gap
    rows.append([name, epochs_run, h.history["loss"][-1], val_acc.max(), conv, gap, test_acc, elapsed])
    print(f"{name:32s} test acc = {test_acc:.4f}")

results = pd.DataFrame(rows, columns=["Technique", "Epochs run", "Final train loss", "Best val acc",
                                      "Epochs to 95% of best", "Train-val gap", "Test acc", "Time (s)"])
display(results.round(4))

# %% [markdown]
# ## 4. Curves

# %%
fig, ax = plt.subplots(1, 2, figsize=(16, 5))
for name, h in hist.items():
    ax[0].plot(h["loss"], label=name)
    ax[1].plot(h["val_accuracy"], label=name)
ax[0].set_title("Training loss"); ax[1].set_title("Validation accuracy")
for a in ax: a.set_xlabel("Epoch"); a.grid(True)
ax[1].legend(fontsize=8, loc="lower right")
plt.tight_layout(); plt.show()

plt.figure(figsize=(10, 4))
plt.bar(results["Technique"], results["Test acc"])
plt.xticks(rotation=40, ha="right"); plt.ylim(results["Test acc"].min() - 0.02, results["Test acc"].max() + 0.01)
plt.title("Test accuracy (generalization performance)"); plt.tight_layout(); plt.show()

# %% [markdown]
# ## 5. Conclusion
# * **Baseline** overfits: training accuracy keeps rising while validation accuracy stalls (large train-val gap).
# * **Dropout** randomly drops units, reducing co-adaptation and the gap; training is noisier and slower.
# * **L1** drives weights to exactly zero (sparse); **L2** shrinks weights smoothly - both limit model complexity.
# * **Early stopping** halts training when validation loss stops improving and restores the best weights: saves time and avoids overfitting.
# * **Data augmentation** adds variation (rotations, flips), improving robustness. It helps most with small datasets.
# * **Batch Norm** normalizes across the mini-batch, speeds up convergence and permits larger learning rates;
#   **Layer Norm** normalizes across features of each sample, so it is independent of batch size (useful for RNNs/Transformers).
