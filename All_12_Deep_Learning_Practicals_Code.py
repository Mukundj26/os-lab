# ALL 12 DEEP LEARNING PRACTICALS — COMPLETE CODE
# Source: the 12-practical assignment record.
# Run ONE practical section at a time. Each section is independent.
# Install the packages listed at the start of each section before running it.
# Jupyter/Colab commands beginning with ! are kept as comments because this is a .py file.
# Practical 12 contains both model-training code and the FastAPI application code.


########################################################################################
# PRACTICAL 1: Implementation of Backpropagation in Multilayer Neural Networks for Image Classification using MNIST Dataset
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow scikit-learn matplotlib
 
import time
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, Flatten, Dense
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
 
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train, y_train = x_train[:10000], y_train[:10000]
x_test, y_test = x_test[:2000], y_test[:2000]
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
 
model = Sequential([
    Input(shape=(28, 28)),
    Flatten(),
    Dense(128, activation="relu"),
    Dense(128, activation="relu"),
    Dense(128, activation="relu"),
    Dense(10, activation="softmax")
])
model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])
 
start = time.time()
history = model.fit(x_train, y_train, epochs=3, batch_size=128,
                    validation_split=0.1, verbose=1)
mlp_time = time.time() - start
mlp_loss, mlp_acc = model.evaluate(x_test, y_test, verbose=0)
 
# Classical models use flattened input vectors.
xtr = x_train.reshape(len(x_train), -1)
xte = x_test.reshape(len(x_test), -1)
 
lr = LogisticRegression(max_iter=300, solver="lbfgs")
start = time.time()
lr.fit(xtr, y_train)
lr_time = time.time() - start
lr_acc = accuracy_score(y_test, lr.predict(xte))
 
dt = DecisionTreeClassifier(max_depth=25, random_state=42)
start = time.time()
dt.fit(xtr, y_train)
dt_time = time.time() - start
dt_acc = accuracy_score(y_test, dt.predict(xte))
 
print("MLP accuracy:", mlp_acc, "training seconds:", mlp_time)
print("Logistic Regression accuracy:", lr_acc, "training seconds:", lr_time)
print("Decision Tree accuracy:", dt_acc, "training seconds:", dt_time)
 
plt.plot(history.history["loss"], label="Training loss")
plt.plot(history.history["val_loss"], label="Validation loss")
plt.xlabel("Epoch"); plt.ylabel("Cross-entropy loss")
plt.title("MLP Loss Curve"); plt.legend(); plt.grid(); plt.show()

########################################################################################
# PRACTICAL 2: Implementation of Multilayer Perceptron and Comparative Study of Activation Functions using IRIS Dataset
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow scikit-learn matplotlib
 
import time
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, Dense, LeakyReLU, ELU
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
 
iris = load_iris()
X, y = iris.data.astype("float32"), iris.target
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train).astype("float32")
X_val = scaler.transform(X_val).astype("float32")
 
def make_model(kind):
    model = Sequential([Input(shape=(4,)), Dense(16)])
    if kind == "LeakyReLU":
        model.add(LeakyReLU(negative_slope=0.1))
    elif kind == "ELU":
        model.add(ELU(alpha=1.0))
    else:
        model.add(Dense(1)) if False else None
        # Use a separate activation layer to retain one 16-neuron hidden layer.
        model.add(tf.keras.layers.Activation(kind.lower()))
    model.add(Dense(3, activation="softmax"))
    model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    return model
 
results = {}
histories = {}
for activation in ["Sigmoid", "Tanh", "ReLU", "LeakyReLU", "ELU"]:
    tf.keras.backend.clear_session()
    m = make_model(activation)
    start = time.time()
    h = m.fit(X_train, y_train, validation_data=(X_val, y_val),
              epochs=5, batch_size=16, verbose=0)
    elapsed = time.time() - start
    loss, acc = m.evaluate(X_val, y_val, verbose=0)
    results[activation] = (loss, acc, elapsed)
    histories[activation] = h.history["loss"]
    print(activation, "val_loss:", round(loss, 4),
          "val_accuracy:", round(acc, 4), "seconds:", round(elapsed, 2))
 
for name, losses in histories.items():
    plt.plot(losses, label=name)
plt.xlabel("Epoch"); plt.ylabel("Training loss")
plt.title("Activation Function Comparison"); plt.legend(); plt.grid(); plt.show()
 
# Manual forward propagation demonstration for one neuron.
x = np.array([0.5, -0.2, 0.1, 0.7])
w = np.array([0.2, 0.4, -0.3, 0.1])
b = 0.05
z = np.dot(x, w) + b
sigmoid_output = 1 / (1 + np.exp(-z))
print("Manual z:", z, "manual sigmoid output:", sigmoid_output)
 
# Plot activation functions.
z = np.linspace(-5, 5, 300)
plt.plot(z, 1/(1+np.exp(-z)), label="Sigmoid")
plt.plot(z, np.tanh(z), label="Tanh")
plt.plot(z, np.maximum(0,z), label="ReLU")
plt.plot(z, np.where(z > 0, z, 0.1*z), label="Leaky ReLU")
plt.plot(z, np.where(z > 0, z, np.exp(z)-1), label="ELU")
plt.ylim(-2, 5); plt.grid(); plt.legend(); plt.title("Activation Functions"); plt.show()

########################################################################################
# PRACTICAL 3: Implementation and Study of Gradient Problems and Weight Initialization using Fashion-MNIST Dataset
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow matplotlib
 
import time, numpy as np, matplotlib.pyplot as plt, tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, Flatten, Dense
from tensorflow.keras.initializers import RandomNormal, GlorotNormal, HeNormal
from sklearn.model_selection import train_test_split
 
(x_all, y_all), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()
x_all = x_all.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
x_train, x_val, y_train, y_val = train_test_split(
    x_all, y_all, test_size=0.2, random_state=42, stratify=y_all)
 
def build_model(initializer):
    return Sequential([
        Input(shape=(28,28)), Flatten(),
        Dense(256, activation="relu", kernel_initializer=initializer),
        Dense(256, activation="relu", kernel_initializer=initializer),
        Dense(128, activation="relu", kernel_initializer=initializer),
        Dense(128, activation="relu", kernel_initializer=initializer),
        Dense(10, activation="softmax")
    ])
 
initializers = {
    "Small Random": RandomNormal(mean=0.0, stddev=0.01),
    "Xavier": GlorotNormal(),
    "He": HeNormal()
}
histories, scores, gradient_norms = {}, {}, {}
 
# Measure initial gradient norms on the same mini-batch.
xb = tf.convert_to_tensor(x_train[:128])
yb = tf.convert_to_tensor(y_train[:128])
 
for name, init in initializers.items():
    tf.keras.backend.clear_session()
    model = build_model(init)
    model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    with tf.GradientTape() as tape:
        pred = model(xb, training=True)
        loss = tf.keras.losses.sparse_categorical_crossentropy(yb, pred)
        loss = tf.reduce_mean(loss)
    grads = tape.gradient(loss, model.trainable_variables)
    gradient_norms[name] = [
        float(tf.linalg.global_norm(grads[i:i+2]).numpy())
        for i in range(0, len(grads), 2)
    ]
    h = model.fit(x_train, y_train, validation_data=(x_val,y_val),
                  epochs=10, batch_size=128, verbose=0)
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    histories[name] = h.history
    scores[name] = test_acc
    print(name, "test accuracy:", round(test_acc,4),
          "final val accuracy:", round(h.history["val_accuracy"][-1],4))
 
for name, h in histories.items():
    plt.plot(h["loss"], label=name)
plt.xlabel("Epoch"); plt.ylabel("Training loss")
plt.title("Initialization: Training Loss"); plt.legend(); plt.grid(); plt.show()
 
for name, norms in gradient_norms.items():
    plt.plot(range(1, len(norms)+1), norms, marker="o", label=name)
plt.xlabel("Dense layer index"); plt.ylabel("Gradient global norm")
plt.title("Initial Gradient Norms"); plt.legend(); plt.grid(); plt.show()
 
print("Test accuracy comparison:", scores)

########################################################################################
# PRACTICAL 4: Implementation and Comparative Study of Regularization and Normalization Techniques using Fashion-MNIST Dataset
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow matplotlib
 
import time, numpy as np, matplotlib.pyplot as plt, tensorflow as tf
from tensorflow.keras import Sequential, regularizers
from tensorflow.keras.layers import (Input, Flatten, Dense, Dropout,
    BatchNormalization, LayerNormalization, RandomRotation, RandomFlip)
from tensorflow.keras.callbacks import EarlyStopping
 
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
x_train, x_val = x_train[:50000], x_train[50000:]
y_train, y_val = y_train[:50000], y_train[50000:]
 
def build_model(kind):
    layers = [Input(shape=(28,28))]
    if kind == "Augmentation":
        layers += [RandomRotation(0.05), RandomFlip("horizontal")]
    layers += [Flatten()]
    reg = None
    if kind == "L1": reg = regularizers.l1(1e-5)
    if kind == "L2": reg = regularizers.l2(1e-4)
    for units in [256,128,64]:
        layers.append(Dense(units, activation=None, kernel_regularizer=reg))
        if kind == "BatchNorm": layers.append(BatchNormalization())
        if kind == "LayerNorm": layers.append(LayerNormalization())
        layers.append(tf.keras.layers.Activation("relu"))
        if kind == "Dropout": layers.append(Dropout(0.5))
    layers.append(Dense(10, activation="softmax"))
    model = Sequential(layers)
    model.compile(optimizer="adam",
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    return model
 
variants = ["Baseline","Dropout","L1","L2","BatchNorm","LayerNorm","Augmentation"]
histories, results, times = {}, {}, {}
for kind in variants:
    tf.keras.backend.clear_session()
    model = build_model(kind)
    callback = EarlyStopping(monitor="val_loss", patience=5,
                             restore_best_weights=True)
    start = time.time()
    h = model.fit(x_train, y_train, validation_data=(x_val,y_val),
                  epochs=30, batch_size=128, callbacks=[callback], verbose=0)
    times[kind] = time.time()-start
    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    histories[kind] = h.history
    results[kind] = (loss, acc, len(h.history["loss"]))
    print(kind, "test accuracy:", round(acc,4),
          "epochs:", len(h.history["loss"]), "seconds:", round(times[kind],1))
 
for kind, h in histories.items():
    plt.plot(h["val_accuracy"], label=kind)
plt.xlabel("Epoch"); plt.ylabel("Validation accuracy")
plt.title("Normalization and Regularization Comparison")
plt.legend(); plt.grid(); plt.show()
 
print("Results (test loss, test accuracy, epochs):", results)

########################################################################################
# PRACTICAL 5: Comparative Study of CNN Architectures for Image Classification
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow matplotlib
 
import time, numpy as np, matplotlib.pyplot as plt, tensorflow as tf
from tensorflow.keras import layers, Model
 
(x_train,y_train),(x_test,y_test) = tf.keras.datasets.cifar10.load_data()
x_train=x_train.astype("float32")/255.0
x_test=x_test.astype("float32")/255.0
y_train=y_train.flatten(); y_test=y_test.flatten()
x_train,y_train=x_train[:40000],y_train[:40000]
x_val,y_val=x_train[35000:],y_train[35000:]
x_fit,y_fit=x_train[:35000],y_train[:35000]
 
def basic_cnn():
    return tf.keras.Sequential([
        layers.Input((32,32,3)),
        layers.Conv2D(32,3,activation="relu",padding="same"),
        layers.MaxPooling2D(),
        layers.Conv2D(64,3,activation="relu",padding="same"),
        layers.MaxPooling2D(),
        layers.Flatten(), layers.Dense(128,activation="relu"),
        layers.Dense(10,activation="softmax")])
 
def vgg_style():
    return tf.keras.Sequential([
        layers.Input((32,32,3)),
        layers.Conv2D(32,3,padding="same",activation="relu"),
        layers.Conv2D(32,3,padding="same",activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(64,3,padding="same",activation="relu"),
        layers.Conv2D(64,3,padding="same",activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(128,3,padding="same",activation="relu"),
        layers.MaxPooling2D(),
        layers.Flatten(), layers.Dense(128,activation="relu"),
        layers.Dense(10,activation="softmax")])
 
def residual_block(x, filters):
    shortcut=x
    y=layers.Conv2D(filters,3,padding="same",activation="relu")(x)
    y=layers.Conv2D(filters,3,padding="same")(y)
    if x.shape[-1] != filters:
        shortcut=layers.Conv2D(filters,1,padding="same")(shortcut)
    y=layers.Add()([y,shortcut])
    return layers.Activation("relu")(y)
 
def residual_cnn():
    inp=layers.Input((32,32,3))
    x=layers.Conv2D(32,3,padding="same",activation="relu")(inp)
    x=residual_block(x,32)
    x=layers.MaxPooling2D()(x)
    x=residual_block(x,64)
    x=layers.GlobalAveragePooling2D()(x)
    out=layers.Dense(10,activation="softmax")(x)
    return Model(inp,out)
 
builders={"Basic CNN":basic_cnn,"VGG-style CNN":vgg_style,
          "Residual CNN":residual_cnn}
histories={}
for name,builder in builders.items():
    model=builder()
    model.compile(optimizer="adam",loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    start=time.time()
    h=model.fit(x_fit,y_fit,validation_data=(x_val,y_val),
                epochs=5,batch_size=128,verbose=0)
    elapsed=time.time()-start
    loss,acc=model.evaluate(x_test,y_test,verbose=0)
    histories[name]=h.history
    print(name,"test accuracy:",round(acc,4),
          "time:",round(elapsed,1),"sec","test loss:",round(loss,4))
 
for name,h in histories.items():
    plt.plot(h["val_accuracy"],label=name)
plt.xlabel("Epoch"); plt.ylabel("Validation accuracy")
plt.title("CNN Architecture Comparison"); plt.legend(); plt.grid(); plt.show()

########################################################################################
# PRACTICAL 6: Implementation and Performance Analysis of CNN using CIFAR-10 Dataset
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow matplotlib
 
import time, numpy as np, matplotlib.pyplot as plt, tensorflow as tf
from tensorflow.keras import layers, Sequential
 
(x_train,y_train),(x_test,y_test)=tf.keras.datasets.cifar10.load_data()
x_train=x_train.astype("float32")/255.0
x_test=x_test.astype("float32")/255.0
y_train=y_train.flatten(); y_test=y_test.flatten()
 
def make_cnn(kernel=3,stride=1,padding="same",pool="max"):
    Pool=layers.MaxPooling2D if pool=="max" else layers.AveragePooling2D
    return Sequential([
        layers.Input((32,32,3)),
        layers.Conv2D(32,kernel,strides=stride,padding=padding,activation="relu"),
        Pool(pool_size=2),
        layers.Conv2D(64,3,padding="same",activation="relu"),
        Pool(pool_size=2),
        layers.Flatten(),
        layers.Dense(128,activation="relu"),
        layers.Dense(10,activation="softmax")
    ])
 
results=[]
for kernel in [3,5]:
  for stride in [1,2]:
    for padding in ["same","valid"]:
      for pool in ["max","average"]:
        tf.keras.backend.clear_session()
        model=make_cnn(kernel,stride,padding,pool)
        model.compile(optimizer="adam",
            loss="sparse_categorical_crossentropy",metrics=["accuracy"])
        start=time.time()
        h=model.fit(x_train,y_train,epochs=3,batch_size=128,
                    validation_split=0.1,verbose=0)
        elapsed=time.time()-start
        loss,acc=model.evaluate(x_test,y_test,verbose=0)
        results.append((kernel,stride,padding,pool,loss,acc,elapsed))
        print(results[-1])
 
best=max(results,key=lambda row:row[5])
print("Best measured configuration:",best)
 
# Visualize first-layer filters from one trained model.
filters=model.layers[0].get_weights()[0]
fig,axes=plt.subplots(4,8,figsize=(10,5))
for i,ax in enumerate(axes.flat):
    f=filters[:,:,:,i]
    f=(f-f.min())/(f.max()-f.min()+1e-8)
    ax.imshow(f); ax.axis("off")
plt.suptitle("First Convolution Layer Filters"); plt.show()
 
# Feature maps for one test image using the final model.
feature_model=tf.keras.Model(model.input,model.layers[0].output)
maps=feature_model.predict(x_test[:1],verbose=0)[0]
fig,axes=plt.subplots(4,8,figsize=(10,5))
for i,ax in enumerate(axes.flat):
    ax.imshow(maps[:,:,i],cmap="viridis"); ax.axis("off")
plt.suptitle("First-Layer Feature Maps"); plt.show()

########################################################################################
# PRACTICAL 7: Comparative Study of LeNet, AlexNet, VGG16, and ResNet50 using CIFAR-10 Dataset
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow matplotlib
 
import time, numpy as np, matplotlib.pyplot as plt, tensorflow as tf
from tensorflow.keras import layers, Model, Sequential
 
(x_train,y_train),(x_test,y_test)=tf.keras.datasets.cifar10.load_data()
x_train=x_train.astype("float32")/255.0
x_test=x_test.astype("float32")/255.0
y_train=y_train.flatten(); y_test=y_test.flatten()
x_fit,y_fit=x_train[:40000],y_train[:40000]
x_val,y_val=x_train[40000:45000],y_train[40000:45000]
 
def lenet():
 return Sequential([layers.Input((32,32,3)),
  layers.Conv2D(6,5,activation="relu"),layers.AveragePooling2D(),
  layers.Conv2D(16,5,activation="relu"),layers.AveragePooling2D(),
  layers.Flatten(),layers.Dense(120,activation="relu"),
  layers.Dense(84,activation="relu"),layers.Dense(10,activation="softmax")])
 
def alexnet_style():
 return Sequential([layers.Input((32,32,3)),
  layers.Conv2D(64,3,padding="same",activation="relu"),layers.MaxPooling2D(),
  layers.Conv2D(192,3,padding="same",activation="relu"),layers.MaxPooling2D(),
  layers.Conv2D(256,3,padding="same",activation="relu"),
  layers.Flatten(),layers.Dense(256,activation="relu"),
  layers.Dropout(0.5),layers.Dense(10,activation="softmax")])
 
def vgg16_style():
 inp=layers.Input((32,32,3)); x=inp
 for filters,repeats in [(64,2),(128,2),(256,3)]:
  for _ in range(repeats):
   x=layers.Conv2D(filters,3,padding="same",activation="relu")(x)
  x=layers.MaxPooling2D()(x)
 x=layers.Flatten()(x); x=layers.Dense(256,activation="relu")(x)
 out=layers.Dense(10,activation="softmax")(x)
 return Model(inp,out)
 
def resnet50_scratch():
 inp=layers.Input((32,32,3))
 base=tf.keras.applications.ResNet50(include_top=False,weights=None,
                                     input_tensor=inp,pooling="avg")
 out=layers.Dense(10,activation="softmax")(base.output)
 return Model(inp,out)
 
architectures={"LeNet":lenet,"AlexNet-style":alexnet_style,
               "VGG16-style":vgg16_style,"ResNet50-scratch":resnet50_scratch}
histories={}
for name,fn in architectures.items():
 tf.keras.backend.clear_session(); model=fn()
 model.compile(optimizer="adam",loss="sparse_categorical_crossentropy",
               metrics=["accuracy"])
 start=time.time()
 h=model.fit(x_fit,y_fit,validation_data=(x_val,y_val),
             epochs=5,batch_size=128,verbose=0)
 elapsed=time.time()-start
 loss,acc=model.evaluate(x_test,y_test,verbose=0)
 histories[name]=h.history
 print(name,"test accuracy",round(acc,4),"loss",round(loss,4),
       "training seconds",round(elapsed,1))
 
# Transfer learning: resize images to 96x96 and use ImageNet ResNet50.
def resize_batch(images, labels):
    images=tf.image.resize(images,[96,96])
    images=tf.keras.applications.resnet50.preprocess_input(images*255.0)
    return images, labels
train_ds=tf.data.Dataset.from_tensor_slices((x_fit,y_fit)).shuffle(2000).batch(64)
train_ds=train_ds.map(resize_batch).prefetch(tf.data.AUTOTUNE)
val_ds=tf.data.Dataset.from_tensor_slices((x_val,y_val)).batch(64)
val_ds=val_ds.map(resize_batch).prefetch(tf.data.AUTOTUNE)
test_ds=tf.data.Dataset.from_tensor_slices((x_test,y_test)).batch(64)
test_ds=test_ds.map(resize_batch).prefetch(tf.data.AUTOTUNE)
 
base=tf.keras.applications.ResNet50(include_top=False,weights="imagenet",
                                    input_shape=(96,96,3),pooling="avg")
base.trainable=False
inp=layers.Input((96,96,3))
x=base(inp,training=False)
out=layers.Dense(10,activation="softmax")(x)
transfer=Model(inp,out)
transfer.compile(optimizer="adam",loss="sparse_categorical_crossentropy",
                 metrics=["accuracy"])
transfer.fit(train_ds,validation_data=val_ds,epochs=3,verbose=1)
print("Feature extraction test:",transfer.evaluate(test_ds,verbose=0))
 
# Fine-tune last layers (keep BatchNorm layers frozen).
base.trainable=True
for layer in base.layers[:-20]:
    layer.trainable=False
for layer in base.layers:
    if isinstance(layer, layers.BatchNormalization):
        layer.trainable=False
transfer.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
                 loss="sparse_categorical_crossentropy",metrics=["accuracy"])
transfer.fit(train_ds,validation_data=val_ds,epochs=2,verbose=1)
print("Fine-tuned test:",transfer.evaluate(test_ds,verbose=0))

########################################################################################
# PRACTICAL 8: Implementation and Comparative Study of Object Detection Models using Pascal VOC Dataset
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install torch torchvision ultralytics opencv-python matplotlib
 
import time, torch, cv2, numpy as np, matplotlib.pyplot as plt
from PIL import Image
from torchvision.models.detection import (
    fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights,
    ssdlite320_mobilenet_v3_large, SSDLite320_MobileNet_V3_Large_Weights
)
from ultralytics import YOLO
 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
frcnn_weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
ssd_weights = SSDLite320_MobileNet_V3_Large_Weights.DEFAULT
frcnn = fasterrcnn_resnet50_fpn_v2(weights=frcnn_weights).to(device).eval()
ssd = ssdlite320_mobilenet_v3_large(weights=ssd_weights).to(device).eval()
yolo = YOLO("yolov8n.pt")
 
# Use a Pascal VOC 2007 test image URL or upload an image in Colab/Jupyter.
# Example local file: image_path = "sample.jpg"
image_path = "sample.jpg"
image = Image.open(image_path).convert("RGB")
tensor = frcnn_weights.transforms()(image).to(device)
 
@torch.inference_mode()
def torchvision_detect(model, img_tensor, threshold=0.5):
    out = model([img_tensor])[0]
    keep = out["scores"] >= threshold
    return out["boxes"][keep].cpu().numpy(), out["labels"][keep].cpu().numpy(), out["scores"][keep].cpu().numpy()
 
# Inference and approximate latency (warm-up first).
for model in [frcnn, ssd]:
    _ = torchvision_detect(model, tensor)
    start = time.perf_counter()
    for _ in range(10):
        boxes, labels, scores = torchvision_detect(model, tensor)
    latency = (time.perf_counter()-start)/10
    print(type(model).__name__, "latency:", round(latency,4),
          "FPS:", round(1/latency,2), "detections:",len(boxes))
 
# YOLOv8 inference
_ = yolo.predict(source=image_path, verbose=False)
start=time.perf_counter()
for _ in range(10):
    yolo_result=yolo.predict(source=image_path, verbose=False)
yolo_latency=(time.perf_counter()-start)/10
print("YOLOv8n latency:",round(yolo_latency,4),
      "FPS:",round(1/yolo_latency,2))
 
# Display YOLO annotated image.
annotated = yolo_result[0].plot()
plt.figure(figsize=(10,6))
plt.imshow(cv2.cvtColor(annotated,cv2.COLOR_BGR2RGB))
plt.axis("off"); plt.title("YOLOv8 Detection"); plt.show()
 
# Video inference with YOLOv8 (replace with your video file).
# yolo.predict(source="input_video.mp4", save=True, conf=0.25)

########################################################################################
# PRACTICAL 9: Implementation of Semantic Segmentation using U-Net on Oxford-IIIT Pet Dataset
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow tensorflow-datasets matplotlib
 
import tensorflow as tf, tensorflow_datasets as tfds
import numpy as np, matplotlib.pyplot as plt
from tensorflow.keras import layers, Model
 
SIZE=128; BATCH=16; CLASSES=3
(train_raw,val_raw,test_raw),info=tfds.load(
    "oxford_iiit_pet",
    split=["train[:80%]","train[80%:]","test"],
    with_info=True)
 
def preprocess(item):
    image=tf.image.resize(item["image"],[SIZE,SIZE])
    image=tf.cast(image,tf.float32)/255.0
    mask=tf.image.resize(item["segmentation_mask"],[SIZE,SIZE],
                         method="nearest")
    mask=tf.cast(mask,tf.int32)-1
    mask=tf.squeeze(mask,axis=-1)
    return image,mask
 
AUTOTUNE=tf.data.AUTOTUNE
train_ds=train_raw.map(preprocess,num_parallel_calls=AUTOTUNE).shuffle(512).batch(BATCH).prefetch(AUTOTUNE)
val_ds=val_raw.map(preprocess,num_parallel_calls=AUTOTUNE).batch(BATCH).prefetch(AUTOTUNE)
test_ds=test_raw.map(preprocess,num_parallel_calls=AUTOTUNE).batch(BATCH).prefetch(AUTOTUNE)
 
def conv_block(x,f):
    x=layers.Conv2D(f,3,padding="same",kernel_initializer="he_normal")(x)
    x=layers.BatchNormalization()(x); x=layers.Activation("relu")(x)
    x=layers.Conv2D(f,3,padding="same",kernel_initializer="he_normal")(x)
    x=layers.BatchNormalization()(x); return layers.Activation("relu")(x)
 
def build_unet():
    inp=layers.Input((SIZE,SIZE,3))
    c1=conv_block(inp,32); p1=layers.MaxPooling2D()(c1)
    c2=conv_block(p1,64); p2=layers.MaxPooling2D()(c2)
    c3=conv_block(p2,128); p3=layers.MaxPooling2D()(c3)
    c4=conv_block(p3,256); p4=layers.MaxPooling2D()(c4)
    b=conv_block(p4,512)
    u=layers.Conv2DTranspose(256,2,strides=2,padding="same")(b)
    u=layers.Concatenate()([u,c4]); c=conv_block(u,256)
    u=layers.Conv2DTranspose(128,2,strides=2,padding="same")(c)
    u=layers.Concatenate()([u,c3]); c=conv_block(u,128)
    u=layers.Conv2DTranspose(64,2,strides=2,padding="same")(c)
    u=layers.Concatenate()([u,c2]); c=conv_block(u,64)
    u=layers.Conv2DTranspose(32,2,strides=2,padding="same")(c)
    u=layers.Concatenate()([u,c1]); c=conv_block(u,32)
    out=layers.Conv2D(CLASSES,1,activation="softmax")(c)
    return Model(inp,out)
 
model=build_unet()
model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
              loss="sparse_categorical_crossentropy",metrics=["accuracy"])
history=model.fit(train_ds,validation_data=val_ds,epochs=10)
 
# Confusion matrix over all test pixels.
cm=np.zeros((CLASSES,CLASSES),dtype=np.int64)
for images,masks in test_ds:
    pred=np.argmax(model.predict(images,verbose=0),axis=-1)
    batch_cm=tf.math.confusion_matrix(
        tf.reshape(masks,[-1]),tf.reshape(pred,[-1]),
        num_classes=CLASSES).numpy()
    cm += batch_cm
tp=np.diag(cm).astype(float)
actual=cm.sum(axis=1); predicted=cm.sum(axis=0)
iou=tp/np.maximum(actual+predicted-tp,1)
dice=2*tp/np.maximum(actual+predicted,1)
pixel_acc=tp.sum()/max(cm.sum(),1)
print("Pixel Accuracy:",pixel_acc)
print("Per-class IoU:",iou,"Mean IoU:",iou.mean())
print("Per-class Dice:",dice,"Mean Dice:",dice.mean())
 
images,masks=next(iter(test_ds))
pred=np.argmax(model.predict(images,verbose=0),axis=-1)
fig,axes=plt.subplots(3,3,figsize=(9,9))
for i in range(3):
    axes[i,0].imshow(images[i]); axes[i,0].set_title("Image")
    axes[i,1].imshow(masks[i],vmin=0,vmax=2); axes[i,1].set_title("Ground truth")
    axes[i,2].imshow(pred[i],vmin=0,vmax=2); axes[i,2].set_title("Prediction")
    for ax in axes[i]: ax.axis("off")
plt.tight_layout(); plt.show()

########################################################################################
# PRACTICAL 10: Implementation of Stock Market Time-Series Forecasting using RNN
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install yfinance tensorflow scikit-learn matplotlib
 
import yfinance as yf, numpy as np, pandas as pd, matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error,mean_squared_error
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input,SimpleRNN,Dense,Dropout
 
ticker="TCS.NS"
data=yf.download(ticker,period="5y",auto_adjust=False,progress=False)
if isinstance(data.columns,pd.MultiIndex):
    data.columns=data.columns.get_level_values(0)
data=data[["Open","High","Low","Close","Volume"]].dropna()
data["Close"].plot(figsize=(12,4),title=ticker+" Closing Price"); plt.grid(); plt.show()
 
values=data.values.astype("float32")
split=int(len(values)*0.8)
x_scaler=MinMaxScaler().fit(values[:split])
y_scaler=MinMaxScaler().fit(values[:split,3].reshape(-1,1))
sx=x_scaler.transform(values)
sy=y_scaler.transform(values[:,3].reshape(-1,1))
 
window=30; Xtr=[]; ytr=[]; Xte=[]; yte=[]
for i in range(window,len(sx)):
    seq=sx[i-window:i]; target=sy[i]
    if i<split: Xtr.append(seq); ytr.append(target)
    else: Xte.append(seq); yte.append(target)
Xtr=np.array(Xtr); ytr=np.array(ytr)
Xte=np.array(Xte); yte=np.array(yte)
 
model=Sequential([Input((window,5)),SimpleRNN(50,activation="tanh"),
                  Dropout(0.2),Dense(1)])
model.compile(optimizer="adam",loss="mse",metrics=["mae"])
history=model.fit(Xtr,ytr,epochs=20,batch_size=32,
                  validation_split=0.1,shuffle=False)
plt.plot(history.history["loss"],label="train")
plt.plot(history.history["val_loss"],label="validation")
plt.legend(); plt.title("RNN Loss"); plt.grid(); plt.show()
 
pred_scaled=model.predict(Xte,verbose=0)
pred=y_scaler.inverse_transform(pred_scaled)
actual=y_scaler.inverse_transform(yte)
print("MAE:",mean_absolute_error(actual,pred))
print("RMSE:",np.sqrt(mean_squared_error(actual,pred)))
plt.figure(figsize=(12,4)); plt.plot(actual,label="Actual")
plt.plot(pred,label="Predicted"); plt.legend(); plt.grid()
plt.title("Actual vs Predicted Closing Price"); plt.show()

########################################################################################
# PRACTICAL 11: Implementation and Comparative Analysis of GRU for Stock Market Forecasting
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install yfinance tensorflow scikit-learn matplotlib
 
import time, yfinance as yf, numpy as np, pandas as pd, matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error,mean_squared_error
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input,SimpleRNN,GRU,Dense,Dropout
 
ticker="TCS.NS"
data=yf.download(ticker,period="5y",auto_adjust=False,progress=False)
if isinstance(data.columns,pd.MultiIndex):
    data.columns=data.columns.get_level_values(0)
data=data[["Open","High","Low","Close","Volume"]].dropna()
values=data.values.astype("float32"); split=int(len(values)*0.8)
xs=MinMaxScaler().fit(values[:split])
ys=MinMaxScaler().fit(values[:split,3].reshape(-1,1))
sx=xs.transform(values); sy=ys.transform(values[:,3].reshape(-1,1))
window=30; Xtr=[]; ytr=[]; Xte=[]; yte=[]
for i in range(window,len(sx)):
    if i<split: Xtr.append(sx[i-window:i]); ytr.append(sy[i])
    else: Xte.append(sx[i-window:i]); yte.append(sy[i])
Xtr=np.array(Xtr); ytr=np.array(ytr); Xte=np.array(Xte); yte=np.array(yte)
actual=ys.inverse_transform(yte)
 
def train_model(kind):
    layer=SimpleRNN(50) if kind=="RNN" else GRU(50)
    model=Sequential([Input((window,5)),layer,Dropout(0.2),Dense(1)])
    model.compile(optimizer="adam",loss="mse",metrics=["mae"])
    start=time.time()
    h=model.fit(Xtr,ytr,epochs=20,batch_size=32,
                validation_split=0.1,shuffle=False,verbose=0)
    elapsed=time.time()-start
    p=ys.inverse_transform(model.predict(Xte,verbose=0))
    mae=mean_absolute_error(actual,p)
    rmse=np.sqrt(mean_squared_error(actual,p))
    return model,h,elapsed,p,mae,rmse
 
rnn=train_model("RNN")
gru=train_model("GRU")
for name,res in [("RNN",rnn),("GRU",gru)]:
    print(name,"time",round(res[2],2),"MAE",round(res[4],3),
          "RMSE",round(res[5],3))
 
plt.plot(rnn[1].history["loss"],label="RNN")
plt.plot(gru[1].history["loss"],label="GRU")
plt.xlabel("Epoch"); plt.ylabel("Training MSE"); plt.legend()
plt.title("RNN vs GRU Training Loss"); plt.grid(); plt.show()
 
plt.figure(figsize=(12,4))
plt.plot(actual,label="Actual")
plt.plot(rnn[3],label="RNN")
plt.plot(gru[3],label="GRU")
plt.legend(); plt.title("RNN vs GRU Forecast"); plt.grid(); plt.show()

########################################################################################
# PRACTICAL 12: Handwritten Digit Classification using Deep Learning and REST API Deployment
# Run this section independently; do not run all sections sequentially.
########################################################################################

# !pip -q install tensorflow fastapi uvicorn python-multipart pillow requests matplotlib
 
import tensorflow as tf, numpy as np, matplotlib.pyplot as plt
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input,Dense
 
(x_train,y_train),(x_test,y_test)=tf.keras.datasets.mnist.load_data()
x_train=x_train.astype("float32").reshape(-1,784)/255.0
x_test=x_test.astype("float32").reshape(-1,784)/255.0
 
model=Sequential([
    Input(shape=(784,)),
    Dense(128,activation="relu"),
    Dense(64,activation="relu"),
    Dense(10,activation="softmax")
])
model.compile(optimizer="adam",
    loss="sparse_categorical_crossentropy",metrics=["accuracy"])
history=model.fit(x_train,y_train,epochs=5,batch_size=128,
                  validation_split=0.1)
loss,accuracy=model.evaluate(x_test,y_test,verbose=0)
print("Test loss:",loss,"Test accuracy:",accuracy)
model.save("mnist_model.keras")
 
pred=model.predict(x_test[:10],verbose=0).argmax(axis=1)
print("Actual:",y_test[:10])
print("Predicted:",pred)
from fastapi import FastAPI, UploadFile, File, HTTPException
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import io
 
app = FastAPI(title="MNIST Digit Recognition API")
model = load_model("mnist_model.keras")
 
@app.get("/")
def home():
    return {"message": "MNIST Digit Recognition API is running"}
 
@app.post("/predict")
async def predict_digit(file: UploadFile = File(...)):
    try:
        raw = await file.read()
        image = Image.open(io.BytesIO(raw)).convert("L")
        image = ImageOps.fit(image, (28, 28))
        arr = np.asarray(image).astype("float32")
 
        # MNIST convention: dark digit on a light background.
        if arr.mean() > 127:
            arr = 255.0 - arr
 
        arr = arr / 255.0
        arr = arr.reshape(1, 784)
 
        probabilities = model.predict(arr, verbose=0)[0]
        digit = int(np.argmax(probabilities))
        confidence = float(np.max(probabilities))
 
        return {
            "predicted_digit": digit,
            "confidence": round(confidence, 4)
        }
    except Exception as exc:
        raise HTTPException(status_code=400,
                            detail=f"Could not process image: {exc}")
# Optional notebook client test, while the API server is running:
import requests
url = "http://127.0.0.1:8000/predict"
with open("digit.png", "rb") as f:
    response = requests.post(url, files={"file": ("digit.png", f, "image/png")})
print(response.status_code, response.json())
