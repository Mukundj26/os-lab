# %% [markdown]
# # Practical 9: Semantic Segmentation using U-Net (Oxford-IIIT Pet) - CO1, CO2, CO4
# **Aim:** Load images and masks, build a U-Net for pixel-wise classification, visualize predicted vs ground-truth
# masks, and evaluate IoU, Dice coefficient and pixel accuracy.
#
# Install once: `pip install tensorflow-datasets`

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow import keras
from tensorflow.keras import layers

SEED = 42
tf.keras.utils.set_random_seed(SEED)
IMG_SIZE = 128
BATCH = 32
EPOCHS = 10
NUM_CLASSES = 3          # 0 = pet, 1 = background, 2 = border

# %% [markdown]
# ## 1. Load and pre-process the dataset
# Masks contain labels 1, 2, 3 -> shifted to 0, 1, 2. Images are resized and scaled to [0, 1].

# %%
dataset, info = tfds.load("oxford_iiit_pet:3.*.*", with_info=True)

def preprocess(sample):
    image = tf.image.resize(sample["image"], (IMG_SIZE, IMG_SIZE)) / 255.0
    mask = tf.image.resize(sample["segmentation_mask"], (IMG_SIZE, IMG_SIZE), method="nearest")
    mask = tf.cast(mask, tf.int32) - 1
    return image, mask

def augment(image, mask):
    flip = tf.random.uniform(()) > 0.5
    image = tf.cond(flip, lambda: tf.image.flip_left_right(image), lambda: image)
    mask = tf.cond(flip, lambda: tf.image.flip_left_right(mask), lambda: mask)
    return image, mask

train_full = dataset["train"].map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)
test_ds = dataset["test"].map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)

n_train = info.splits["train"].num_examples
n_val = int(0.1 * n_train)
val_ds = train_full.take(n_val).batch(BATCH).prefetch(tf.data.AUTOTUNE)
train_ds = (train_full.skip(n_val).map(augment, num_parallel_calls=tf.data.AUTOTUNE)
            .shuffle(500, seed=SEED).batch(BATCH).prefetch(tf.data.AUTOTUNE))
test_batches = test_ds.batch(BATCH).prefetch(tf.data.AUTOTUNE)
print("train:", n_train - n_val, "val:", n_val, "test:", info.splits["test"].num_examples)

# %% [markdown]
# ## 2. U-Net model
# Encoder (conv + max-pool) -> bottleneck -> decoder (transposed conv + **skip connections**) -> 1x1 conv with softmax.

# %%
def conv_block(x, filters):
    x = layers.Conv2D(filters, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(filters, 3, padding="same", activation="relu")(x)
    return x

def build_unet(input_shape=(IMG_SIZE, IMG_SIZE, 3), num_classes=NUM_CLASSES):
    inputs = layers.Input(input_shape)
    # encoder
    c1 = conv_block(inputs, 32); p1 = layers.MaxPooling2D()(c1)
    c2 = conv_block(p1, 64);     p2 = layers.MaxPooling2D()(c2)
    c3 = conv_block(p2, 128);    p3 = layers.MaxPooling2D()(c3)
    c4 = conv_block(p3, 256);    p4 = layers.MaxPooling2D()(c4)
    # bottleneck
    b = conv_block(p4, 512)
    b = layers.Dropout(0.3)(b)
    # decoder with skip connections
    u4 = layers.Conv2DTranspose(256, 2, strides=2, padding="same")(b)
    c5 = conv_block(layers.concatenate([u4, c4]), 256)
    u3 = layers.Conv2DTranspose(128, 2, strides=2, padding="same")(c5)
    c6 = conv_block(layers.concatenate([u3, c3]), 128)
    u2 = layers.Conv2DTranspose(64, 2, strides=2, padding="same")(c6)
    c7 = conv_block(layers.concatenate([u2, c2]), 64)
    u1 = layers.Conv2DTranspose(32, 2, strides=2, padding="same")(c7)
    c8 = conv_block(layers.concatenate([u1, c1]), 32)
    outputs = layers.Conv2D(num_classes, 1, activation="softmax")(c8)
    return keras.Model(inputs, outputs, name="U-Net")

model = build_unet()
model.compile(optimizer=keras.optimizers.Adam(1e-3),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.summary()

# %% [markdown]
# ## 3. Train

# %%
history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS,
                    callbacks=[keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)])

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(history.history["loss"], label="train"); ax[0].plot(history.history["val_loss"], label="val")
ax[0].set_title("Loss"); ax[0].legend()
ax[1].plot(history.history["accuracy"], label="train"); ax[1].plot(history.history["val_accuracy"], label="val")
ax[1].set_title("Pixel accuracy"); ax[1].legend()
plt.show()

# %% [markdown]
# ## 4. Evaluation: IoU, Dice coefficient, pixel accuracy
# Computed over the whole test set from the confusion matrix (per class and mean).

# %%
conf = np.zeros((NUM_CLASSES, NUM_CLASSES), dtype=np.int64)
for images, masks in test_batches:
    pred = np.argmax(model.predict(images, verbose=0), axis=-1).ravel()
    true = masks.numpy().squeeze(-1).ravel()
    conf += tf.math.confusion_matrix(true, pred, num_classes=NUM_CLASSES).numpy()

tp = np.diag(conf).astype(float)
fp = conf.sum(axis=0) - tp
fn = conf.sum(axis=1) - tp
iou = tp / (tp + fp + fn + 1e-9)
dice = 2 * tp / (2 * tp + fp + fn + 1e-9)
pixel_acc = tp.sum() / conf.sum()

names = ["Pet", "Background", "Border"]
metrics = pd.DataFrame({"Class": names, "IoU": iou, "Dice": dice})
display(metrics.round(4))
print(f"Mean IoU      : {iou.mean():.4f}")
print(f"Mean Dice     : {dice.mean():.4f}")
print(f"Pixel accuracy: {pixel_acc:.4f}")

# %% [markdown]
# ## 5. Visualize predicted masks vs ground truth

# %%
images, masks = next(iter(test_batches))
preds = np.argmax(model.predict(images, verbose=0), axis=-1)
n = 5
plt.figure(figsize=(12, 3 * n))
for i in range(n):
    for j, (img, title, cmap) in enumerate([
            (images[i], "Input image", None),
            (masks[i].numpy().squeeze(), "Ground truth mask", "viridis"),
            (preds[i], "Predicted mask", "viridis")]):
        plt.subplot(n, 3, i * 3 + j + 1)
        plt.imshow(img, cmap=cmap, vmin=0 if cmap else None, vmax=2 if cmap else None)
        plt.title(title); plt.axis("off")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6. Conclusion
# * The U-Net encoder captures context while the decoder restores resolution; **skip connections** bring back fine
#   spatial detail so object boundaries are sharper.
# * **Pixel accuracy** is optimistic because background dominates; **IoU** and **Dice** are more reliable.
# * The thin **border** class is hardest (lowest IoU), as expected for small, narrow regions.
# * Accuracy can be improved with more epochs, a larger input size, a pre-trained encoder (e.g. MobileNetV2)
#   or a Dice/Focal loss.
