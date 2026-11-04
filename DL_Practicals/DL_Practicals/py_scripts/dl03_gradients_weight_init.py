# %% [markdown]
# # Practical 3: Gradient Problems and Weight Initialization (Fashion-MNIST) - CO1, CO2
# **Aim:** Show vanishing/exploding gradients with poor initialization and compare Xavier and He initialization
# using gradient norms per layer, training loss and validation accuracy.

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras

SEED = 42
tf.keras.utils.set_random_seed(SEED)

# %% [markdown]
# ## 1. Load, normalize and split (train / validation / test)

# %%
(x_train_full, y_train_full), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()
x_train_full = x_train_full.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
x_train, y_train = x_train_full[:50000], y_train_full[:50000]
x_val, y_val = x_train_full[50000:], y_train_full[50000:]
print(x_train.shape, x_val.shape, x_test.shape)

# %% [markdown]
# ## 2. Deep MLP builder
# 8 hidden layers of 128 neurons. Sigmoid shows vanishing gradients clearly; ReLU is used for the He/large-init test.

# %%
def build_model(kernel_init, activation="sigmoid", depth=8, units=128):
    layers = [keras.layers.Input(shape=(28, 28)), keras.layers.Flatten()]
    for _ in range(depth):
        layers.append(keras.layers.Dense(units, activation=activation, kernel_initializer=kernel_init))
    layers.append(keras.layers.Dense(10, activation="softmax"))
    m = keras.Sequential(layers)
    m.compile(optimizer=keras.optimizers.SGD(learning_rate=0.05),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return m

def gradient_norms(model, x, y):
    """L2 norm of the loss gradient w.r.t. the kernel of every Dense layer."""
    with tf.GradientTape() as tape:
        loss = keras.losses.sparse_categorical_crossentropy(y, model(x, training=True))
        loss = tf.reduce_mean(loss)
    dense = [l for l in model.layers if isinstance(l, keras.layers.Dense)]
    grads = tape.gradient(loss, [l.kernel for l in dense])
    return [float(tf.norm(g)) for g in grads]

# %% [markdown]
# ## 3. Experiment configurations
# * **Small random** (std = 0.01): signals shrink layer by layer -> vanishing gradients (sigmoid).
# * **Large random** (std = 1.0, ReLU): signals grow layer by layer -> exploding gradients.
# * **Xavier/Glorot** (sigmoid) and **He** (ReLU): variance-preserving, stable training.

# %%
configs = {
    "Small random (sigmoid)": (keras.initializers.RandomNormal(stddev=0.01), "sigmoid"),
    "Large random (ReLU)":    (keras.initializers.RandomNormal(stddev=1.0),  "relu"),
    "Xavier (sigmoid)":       (keras.initializers.GlorotUniform(),  "sigmoid"),
    "He (ReLU)":              (keras.initializers.HeNormal(),       "relu"),
}

results, hist, norms_before, norms_after = [], {}, {}, {}
for name, (init, act) in configs.items():
    tf.keras.utils.set_random_seed(SEED)
    model = build_model(init, act)
    xb, yb = x_train[:512], y_train[:512]
    norms_before[name] = gradient_norms(model, xb, yb)           # at initialization
    h = model.fit(x_train, y_train, validation_data=(x_val, y_val),
                  epochs=10, batch_size=128, verbose=0)
    norms_after[name] = gradient_norms(model, xb, yb)
    hist[name] = h.history
    test_acc = model.evaluate(x_test, y_test, verbose=0)[1]
    loss_last = h.history["loss"][-1]
    results.append([name, loss_last if np.isfinite(loss_last) else float("nan"),
                    h.history["val_accuracy"][-1], test_acc])
    print(f"{name}: done")

display(pd.DataFrame(results, columns=["Configuration", "Final train loss", "Val accuracy", "Test accuracy"]).round(4))

# %% [markdown]
# ## 4. Gradient norm per layer (at initialization)
# Layer 1 = closest to the input. A steep drop toward layer 1 means vanishing gradients; a rise means exploding.

# %%
fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
for name, n in norms_before.items():
    ax[0].plot(range(1, len(n) + 1), n, marker="o", label=name)
for name, n in norms_after.items():
    ax[1].plot(range(1, len(n) + 1), n, marker="o", label=name)
for a, t in zip(ax, ["Gradient norms at initialization", "Gradient norms after 10 epochs"]):
    a.set_yscale("log"); a.set_xlabel("Layer (1 = first hidden)"); a.set_ylabel("||grad||")
    a.set_title(t); a.legend(fontsize=8); a.grid(True, which="both", alpha=0.3)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 5. Training loss and validation accuracy

# %%
fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
for name, h in hist.items():
    ax[0].plot(h["loss"], label=name); ax[1].plot(h["val_accuracy"], label=name)
ax[0].set_title("Training loss"); ax[1].set_title("Validation accuracy")
for a in ax: a.set_xlabel("Epoch"); a.legend(fontsize=8); a.grid(True)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6. Conclusion
# * Very small random weights with sigmoid make gradients shrink exponentially toward the input layers
#   (vanishing gradients): the loss barely moves and accuracy stays low.
# * Very large weights make activations and gradients blow up (exploding gradients), giving unstable or NaN loss.
# * Xavier initialization keeps variance stable for sigmoid/tanh; He initialization does this for ReLU.
# * With proper initialization, gradient norms are similar across layers, loss falls smoothly and
#   validation accuracy is clearly higher, so training is stable.
