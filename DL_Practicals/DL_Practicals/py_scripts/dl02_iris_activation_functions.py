# %% [markdown]
# # Practical 2: MLP and Comparative Study of Activation Functions (IRIS)
# **Aim:** Build an MLP (1 hidden layer, 16 neurons), implement manual forward propagation, and compare
# Sigmoid, Tanh, ReLU, Leaky ReLU and ELU.

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

tf.keras.utils.set_random_seed(42)

# %% [markdown]
# ## 1. Load and normalize the IRIS dataset

# %%
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler().fit(X_train)
X_train, X_val = scaler.transform(X_train), scaler.transform(X_val)
print(X_train.shape, X_val.shape)

# %% [markdown]
# ## 2. Plot the activation functions

# %%
z = np.linspace(-5, 5, 400)
acts = {
    "Sigmoid": 1 / (1 + np.exp(-z)),
    "Tanh": np.tanh(z),
    "ReLU": np.maximum(0, z),
    "Leaky ReLU": np.where(z > 0, z, 0.01 * z),
    "ELU": np.where(z > 0, z, 1.0 * (np.exp(z) - 1)),
}
fig, axes = plt.subplots(1, 5, figsize=(20, 3.5))
for ax, (name, val) in zip(axes, acts.items()):
    ax.plot(z, val); ax.set_title(name); ax.grid(True); ax.axhline(0, color="k", lw=0.5)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 3. Manual forward propagation (NumPy)
# Computes  `a1 = f(X W1 + b1)` , `out = softmax(a1 W2 + b2)`  with random weights, to show what Keras does internally.

# %%
def softmax(s):
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

rng = np.random.default_rng(42)
W1, b1 = rng.normal(0, 0.5, (4, 16)), np.zeros(16)
W2, b2 = rng.normal(0, 0.5, (16, 3)), np.zeros(3)

def manual_forward(X, f):
    hidden = f(X @ W1 + b1)          # hidden layer: 16 neurons
    return softmax(hidden @ W2 + b2)  # output layer: 3 classes

probs = manual_forward(X_train[:5], lambda s: np.maximum(0, s))
print("Manual forward pass (ReLU) class probabilities:\n", probs.round(3))
print("Each row sums to 1:", probs.sum(axis=1).round(3))

# %% [markdown]
# ## 4. Train one Keras model per activation
# Adam (lr=0.001), batch size 16, 5 epochs.

# %%
activations = {
    "Sigmoid": "sigmoid",
    "Tanh": "tanh",
    "ReLU": "relu",
    "Leaky ReLU": keras.layers.LeakyReLU(negative_slope=0.01),
    "ELU": "elu",
}
histories, summary = {}, []
for name, act in activations.items():
    tf.keras.utils.set_random_seed(42)
    model = keras.Sequential([
        keras.layers.Input(shape=(4,)),
        keras.layers.Dense(16, activation=act),
        keras.layers.Dense(3, activation="softmax"),
    ])
    model.compile(optimizer=keras.optimizers.Adam(0.001),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    h = model.fit(X_train, y_train, validation_data=(X_val, y_val),
                  epochs=5, batch_size=16, verbose=0)
    histories[name] = h.history
    loss_drop = h.history["loss"][0] - h.history["loss"][-1]
    summary.append([name, h.history["loss"][-1], h.history["val_accuracy"][-1], loss_drop])

results = pd.DataFrame(summary, columns=["Activation", "Final train loss", "Val accuracy", "Loss drop (convergence)"])
display(results.round(4))

# %% [markdown]
# ## 4b. Manual forward propagation with the TRAINED weights
# The weights learned by Keras are pulled out and the forward pass is recomputed by hand in NumPy.
# The result must match `model.predict`, which proves the network is just `softmax(relu(X W1 + b1) W2 + b2)`.

# %%
tf.keras.utils.set_random_seed(42)
check = keras.Sequential([
    keras.layers.Input(shape=(4,)),
    keras.layers.Dense(16, activation="relu"),
    keras.layers.Dense(3, activation="softmax"),
])
check.compile(optimizer=keras.optimizers.Adam(0.001), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
check.fit(X_train, y_train, epochs=5, batch_size=16, verbose=0)

tW1, tb1 = check.layers[0].get_weights()          # (4, 16) and (16,)
tW2, tb2 = check.layers[1].get_weights()          # (16, 3) and (3,)
manual_out = softmax(np.maximum(0, X_val @ tW1 + tb1) @ tW2 + tb2)
keras_out = check.predict(X_val, verbose=0)
print("Max |manual - keras| :", np.abs(manual_out - keras_out).max())
print("Manual accuracy      :", (manual_out.argmax(axis=1) == y_val).mean())
print("Keras accuracy       :", (keras_out.argmax(axis=1) == y_val).mean())

# %% [markdown]
# ## 5. Compare training loss, validation accuracy and convergence speed

# %%
fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
for name, h in histories.items():
    ax[0].plot(range(1, 6), h["loss"], marker="o", label=name)
    ax[1].plot(range(1, 6), h["val_accuracy"], marker="o", label=name)
ax[0].set_title("Training loss"); ax[1].set_title("Validation accuracy")
for a in ax: a.set_xlabel("Epoch"); a.legend(); a.grid(True)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6. Conclusion
# | Activation | Advantages | Limitations |
# |---|---|---|
# | Sigmoid | Smooth, outputs in (0,1) | Vanishing gradients, not zero-centred, slow convergence |
# | Tanh | Zero-centred, stronger gradients than sigmoid | Still saturates for large \|x\| |
# | ReLU | Cheap, no saturation for x>0, fast convergence | "Dying ReLU" (zero gradient for x<0) |
# | Leaky ReLU | Fixes dying ReLU with small negative slope | Slope is a hyper-parameter |
# | ELU | Smooth, negative values push mean activation to zero | Exponential is more costly |
#
# With only 5 epochs the ReLU-family activations (ReLU, Leaky ReLU, ELU) normally lower the loss fastest,
# whereas Sigmoid is slowest. Results vary slightly with the random seed.
