# %% [markdown]
# # Practical 1: Backpropagation in a Multilayer Neural Network (MNIST)
# **Aim:** Train an MLP (3 hidden layers x 128, ReLU, Softmax) on 10,000 MNIST training images,
# test on 2,000 images, and compare with Logistic Regression and a Decision Tree.

# %%
import time
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

tf.keras.utils.set_random_seed(42)

# %% [markdown]
# ## 1. Load and pre-process data
# Pixels are scaled to [0, 1]; images are flattened to 784 features for the MLP.

# %%
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
x_train, y_train = x_train[:10000], y_train[:10000]      # 10,000 training images
x_test, y_test = x_test[:2000], y_test[:2000]            # 2,000 test images

x_train = (x_train.astype("float32") / 255.0).reshape(-1, 784)
x_test = (x_test.astype("float32") / 255.0).reshape(-1, 784)
print("Train:", x_train.shape, "Test:", x_test.shape)

plt.figure(figsize=(8, 2))
for i in range(8):
    plt.subplot(1, 8, i + 1)
    plt.imshow(x_train[i].reshape(28, 28), cmap="gray")
    plt.title(y_train[i]); plt.axis("off")
plt.show()

# %% [markdown]
# ## 2. MLP: 3 hidden layers (128 neurons, ReLU) + Softmax output
# Backpropagation is performed automatically by Keras (gradient of cross-entropy w.r.t. every weight).

# %%
model = keras.Sequential([
    keras.layers.Input(shape=(784,)),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dense(10, activation="softmax"),
])
model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.summary()

t0 = time.time()
history = model.fit(x_train, y_train, epochs=3, batch_size=128,
                    validation_split=0.1, verbose=1)
mlp_time = time.time() - t0
mlp_loss, mlp_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"MLP test accuracy: {mlp_acc:.4f} | training time: {mlp_time:.2f}s")

# %% [markdown]
# ## 3. Baselines: Logistic Regression and Decision Tree

# %%
t0 = time.time()
logreg = LogisticRegression(max_iter=200)
logreg.fit(x_train, y_train)
lr_time = time.time() - t0
lr_acc = accuracy_score(y_test, logreg.predict(x_test))

t0 = time.time()
tree = DecisionTreeClassifier(random_state=42)
tree.fit(x_train, y_train)
dt_time = time.time() - t0
dt_acc = accuracy_score(y_test, tree.predict(x_test))

# %% [markdown]
# ## 4. Comparison and loss curves

# %%
import pandas as pd
results = pd.DataFrame({
    "Model": ["MLP (3x128, Adam)", "Logistic Regression", "Decision Tree"],
    "Test accuracy": [mlp_acc, lr_acc, dt_acc],
    "Training time (s)": [mlp_time, lr_time, dt_time],
})
display(results.round(4))

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].plot(history.history["loss"], marker="o", label="Training loss")
ax[0].plot(history.history["val_loss"], marker="o", label="Validation loss")
ax[0].set_title("MLP loss curves"); ax[0].set_xlabel("Epoch"); ax[0].legend()
ax[1].plot(history.history["accuracy"], marker="o", label="Training accuracy")
ax[1].plot(history.history["val_accuracy"], marker="o", label="Validation accuracy")
ax[1].set_title("MLP accuracy curves"); ax[1].set_xlabel("Epoch"); ax[1].legend()
ax[2].bar(results["Model"], results["Test accuracy"], color=["tab:blue", "tab:orange", "tab:green"])
ax[2].set_ylim(0.5, 1.0); ax[2].set_title("Test accuracy"); plt.xticks(rotation=15)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 5. Conclusion
# * The MLP learns non-linear features through backpropagation and reaches high accuracy in only 3 epochs.
# * Logistic Regression is a linear model: strong baseline but cannot capture non-linear structure.
# * The Decision Tree is fast to train but overfits raw pixels and generalizes worst.
# * Loss decreases every epoch, showing gradient descent (Adam) is converging.
# * Trade-off: the MLP needs more computation than the classical models for the accuracy gain.
