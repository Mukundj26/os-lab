# %% [markdown]
# # Practical 12: Handwritten Digit Classification and REST API Deployment - CO1, CO2, CO4
# **Aim:** Train a Keras Sequential network on MNIST (784 -> 128 -> 64 -> 10), save it, and serve it through a
# REST API (Flask) that accepts an image and returns the predicted digit (0-9).
#
# Install once: `pip install flask pillow requests`

# %%
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

tf.keras.utils.set_random_seed(42)

# %% [markdown]
# ## 1. Load and pre-process: normalize to [0, 1] and flatten to 784 features

# %%
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
x_train = (x_train.astype("float32") / 255.0).reshape(-1, 784)
x_test = (x_test.astype("float32") / 255.0).reshape(-1, 784)
print(x_train.shape, x_test.shape)

# %% [markdown]
# ## 2. Model: Input(784) -> Dense(128, ReLU) -> Dense(64, ReLU) -> Dense(10, Softmax)

# %%
model = keras.Sequential([
    layers.Input(shape=(784,)),
    layers.Dense(128, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(10, activation="softmax"),
])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.summary()

history = model.fit(x_train, y_train, epochs=5, batch_size=128, validation_split=0.1)

# %% [markdown]
# ## 3. Evaluate and save the model

# %%
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"Test accuracy: {test_acc:.4f} | Test loss: {test_loss:.4f}")

fig, ax = plt.subplots(1, 3, figsize=(16, 4))
ax[0].plot(history.history["loss"], label="train"); ax[0].plot(history.history["val_loss"], label="val")
ax[0].set_title("Loss"); ax[0].legend()
ax[1].plot(history.history["accuracy"], label="train"); ax[1].plot(history.history["val_accuracy"], label="val")
ax[1].set_title("Accuracy"); ax[1].legend()
cm = confusion_matrix(y_test, np.argmax(model.predict(x_test, verbose=0), axis=1))
ConfusionMatrixDisplay(cm).plot(ax=ax[2], colorbar=False); ax[2].set_title("Confusion matrix")
plt.tight_layout(); plt.show()

model.save("mnist_model.keras")
print("Model saved as mnist_model.keras")

# %% [markdown]
# ## 4. REST API code (Flask)
# This cell writes `app.py`. The API:
# * `GET  /`         -> health check
# * `POST /predict`  -> form-data field **`image`** (PNG/JPG). Returns the digit and class probabilities.
#
# Images are converted to grayscale, resized to 28x28, scaled to [0, 1] and flattened. If the picture has a light
# background with a dark digit (e.g. drawn in Paint), it is inverted automatically because MNIST is white-on-black.

# %%
from pathlib import Path

Path("app.py").write_text('''
import io
import numpy as np
from flask import Flask, request, jsonify
from PIL import Image, ImageOps
from tensorflow import keras

app = Flask(__name__)
model = keras.models.load_model("mnist_model.keras")


def preprocess(file_bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert("L")      # grayscale
    img = img.resize((28, 28))
    arr = np.array(img, dtype="float32")
    if arr.mean() > 127:                                       # light background -> invert
        arr = 255.0 - arr
    return (arr / 255.0).reshape(1, 784)


@app.route("/")
def home():
    return jsonify(message="MNIST digit classifier API", usage="POST an image to /predict with form field 'image'")


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify(error="send an image file in the form field 'image'"), 400
    try:
        x = preprocess(request.files["image"].read())
    except Exception as exc:
        return jsonify(error=f"could not read image: {exc}"), 400
    probs = model.predict(x, verbose=0)[0]
    digit = int(np.argmax(probs))
    return jsonify(predicted_digit=digit, confidence=round(float(probs[digit]), 4),
                   probabilities={str(i): round(float(p), 4) for i, p in enumerate(probs)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
'''.strip() + "\n")
print("app.py written")

# %% [markdown]
# ## 5. Run and test the API
# **Option A - from a terminal (recommended for the practical):**
# ```
# python app.py
# curl -X POST -F "image=@digit.png" http://127.0.0.1:5000/predict
# ```
# **Option B - inside this notebook:** the cell below starts the server in a background thread and sends a test image.

# %%
import io, threading, time, requests
from PIL import Image

def start_server():
    import runpy
    ns = runpy.run_path("app.py", run_name="not_main")      # load the app without starting it
    ns["app"].run(host="127.0.0.1", port=5000, use_reloader=False)

threading.Thread(target=start_server, daemon=True).start()
time.sleep(8)                                               # give the model time to load

# make a test image from the MNIST test set
idx = 7
img = Image.fromarray((x_test[idx].reshape(28, 28) * 255).astype("uint8"))
buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)

print(requests.get("http://127.0.0.1:5000/").json())
resp = requests.post("http://127.0.0.1:5000/predict", files={"image": ("digit.png", buf, "image/png")})
print("API response:", resp.json())
print("True label  :", y_test[idx])
plt.imshow(img, cmap="gray"); plt.title("Test image sent to API"); plt.axis("off"); plt.show()

# %% [markdown]
# ## 6. Same API with FastAPI (alternative)
# The problem statement allows **FastAPI or Flask**. This cell writes `fastapi_app.py`.
# Install: `pip install fastapi uvicorn python-multipart`. Run from a terminal:
# ```
# uvicorn fastapi_app:app --port 8000
# ```
# Interactive documentation and a test form are generated automatically at http://127.0.0.1:8000/docs
# or use `curl -X POST -F "image=@digit.png" http://127.0.0.1:8000/predict`.

# %%
Path("fastapi_app.py").write_text('''
import io
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
from tensorflow import keras

app = FastAPI(title="MNIST digit classifier API")
model = keras.models.load_model("mnist_model.keras")


def preprocess(file_bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert("L").resize((28, 28))
    arr = np.array(img, dtype="float32")
    if arr.mean() > 127:                       # light background -> invert (MNIST is white on black)
        arr = 255.0 - arr
    return (arr / 255.0).reshape(1, 784)


@app.get("/")
def home():
    return {"message": "MNIST digit classifier API", "usage": "POST an image to /predict"}


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    try:
        x = preprocess(await image.read())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"could not read image: {exc}")
    probs = model.predict(x, verbose=0)[0]
    digit = int(np.argmax(probs))
    return {"predicted_digit": digit, "confidence": round(float(probs[digit]), 4),
            "probabilities": {str(i): round(float(p), 4) for i, p in enumerate(probs)}}
'''.strip() + "\n")
print("fastapi_app.py written")

# %% [markdown]
# ## 7. Conclusion
# * The fully connected network reaches about 97-98% test accuracy after only 5 epochs.
# * The trained model was saved once (`mnist_model.keras`) and reloaded by the API - training is not repeated per request.
# * The REST endpoint makes the model usable from any client (web page, mobile app, `curl`) with a simple HTTP request.
# * Pre-processing in the API must match training (grayscale, 28x28, [0,1], flattened); mismatches are the most common
#   cause of wrong predictions on hand-drawn digits.
