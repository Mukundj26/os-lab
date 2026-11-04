# %% [markdown]
# # Practical 11: Comparative Analysis of GRU for Stock Market Forecasting - CO1, CO2, CO5
# **Aim:** Use the same dataset and preprocessing as Practical 10, implement a GRU (update and reset gates),
# and compare it with the RNN on convergence speed, computational efficiency, prediction performance and loss curves.

# %%
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

SEED = 42
TICKER = "AAPL"
START, END = "2015-01-01", "2025-01-01"
WINDOW = 30
FEATURES = ["Open", "High", "Low", "Close", "Volume"]
EPOCHS = 30

# %% [markdown]
# ## 1. Same data and preprocessing as Practical 10

# %%
try:
    df = yf.download(TICKER, start=START, end=END, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[FEATURES].dropna()
    assert len(df) > 100
except Exception as e:
    print("Yahoo Finance download failed:", e, "-> reading stock.csv")
    df = pd.read_csv("stock.csv", parse_dates=["Date"], index_col="Date")[FEATURES].dropna()

split = int(len(df) * 0.8)
scaler = MinMaxScaler().fit(df.iloc[:split])
scaled = scaler.transform(df)
close_idx = FEATURES.index("Close")

def make_windows(data, window=WINDOW):
    X, y = [], []
    for i in range(window, len(data)):
        X.append(data[i - window:i]); y.append(data[i, close_idx])
    return np.array(X), np.array(y)

X_all, y_all = make_windows(scaled)
cut = split - WINDOW
X_train, y_train, X_test, y_test = X_all[:cut], y_all[:cut], X_all[cut:], y_all[cut:]

def inverse_close(values):
    dummy = np.zeros((len(values), len(FEATURES)))
    dummy[:, close_idx] = np.ravel(values)
    return scaler.inverse_transform(dummy)[:, close_idx]

# %% [markdown]
# ## 2. How a GRU works (manual NumPy forward step)
# For input x_t and previous hidden state h_(t-1):
#
# * Update gate  z_t = sigmoid(W_z x_t + U_z h_(t-1) + b_z)   -> how much of the old state to keep
# * Reset gate   r_t = sigmoid(W_r x_t + U_r h_(t-1) + b_r)   -> how much of the past to forget when building the candidate
# * Candidate    h~_t = tanh(W_h x_t + U_h (r_t * h_(t-1)) + b_h)
# * New state    h_t = z_t * h_(t-1) + (1 - z_t) * h~_t

# %%
def sigmoid(a): return 1 / (1 + np.exp(-a))

def gru_step(x, h_prev, P):
    z = sigmoid(x @ P["Wz"] + h_prev @ P["Uz"] + P["bz"])            # update gate
    r = sigmoid(x @ P["Wr"] + h_prev @ P["Ur"] + P["br"])            # reset gate
    h_cand = np.tanh(x @ P["Wh"] + (r * h_prev) @ P["Uh"] + P["bh"])  # candidate state
    h = z * h_prev + (1 - z) * h_cand
    return h, z, r

rng = np.random.default_rng(SEED)
units = 4
P = {k: rng.normal(0, 0.5, s) for k, s in {
    "Wz": (5, units), "Uz": (units, units), "bz": (units,),
    "Wr": (5, units), "Ur": (units, units), "br": (units,),
    "Wh": (5, units), "Uh": (units, units), "bh": (units,)}.items()}
h = np.zeros(units)
for t in range(WINDOW):
    h, z, r = gru_step(X_train[0, t], h, P)
print("Final hidden state after 30 steps:", h.round(3))
print("Last update gate z:", z.round(3), "| reset gate r:", r.round(3))

# %% [markdown]
# ## 3. Build and train RNN and GRU (50 units each, identical settings)

# %%
def build(kind):
    Layer = layers.SimpleRNN if kind == "RNN" else layers.GRU
    return keras.Sequential([layers.Input(shape=(WINDOW, len(FEATURES))), Layer(50), layers.Dense(1)], name=kind)

results, hists, preds = [], {}, {}
actual = inverse_close(y_test)

for kind in ["RNN", "GRU"]:
    tf.keras.utils.set_random_seed(SEED)
    m = build(kind)
    m.compile(optimizer=keras.optimizers.Adam(0.001), loss="mse")
    t0 = time.time()
    h = m.fit(X_train, y_train, epochs=EPOCHS, batch_size=32, validation_split=0.1, verbose=0)
    train_time = time.time() - t0

    t0 = time.time()
    p = inverse_close(m.predict(X_test, verbose=0))
    infer_time = time.time() - t0

    val = np.array(h.history["val_loss"])
    conv_epoch = int(np.argmax(val <= val.min() * 1.1)) + 1       # first epoch within 10% of best val loss
    preds[kind], hists[kind] = p, h.history
    results.append([kind, m.count_params(), train_time, infer_time, conv_epoch, val.min(),
                    np.sqrt(mean_squared_error(actual, p)), mean_absolute_error(actual, p), r2_score(actual, p)])
    print(kind, "trained")

table = pd.DataFrame(results, columns=["Model", "Parameters", "Train time (s)", "Inference time (s)",
                                       "Epochs to near-best val loss", "Best val loss (scaled)",
                                       "RMSE", "MAE", "R2"])
display(table.round(5))

# %% [markdown]
# ## 4. Loss curves and predictions

# %%
fig, ax = plt.subplots(1, 2, figsize=(15, 4.5))
for kind, h in hists.items():
    ax[0].plot(h["loss"], label=f"{kind} train"); ax[0].plot(h["val_loss"], "--", label=f"{kind} val")
ax[0].set_yscale("log"); ax[0].set_title("Loss curves (log scale)"); ax[0].set_xlabel("Epoch")
ax[0].legend(); ax[0].grid(True, which="both", alpha=0.3)

dates = df.index[split:]
ax[1].plot(dates, actual, label="Actual", color="black")
ax[1].plot(dates, preds["RNN"], label="RNN", alpha=0.8)
ax[1].plot(dates, preds["GRU"], label="GRU", alpha=0.8)
ax[1].set_title("Actual vs predicted close"); ax[1].legend(); ax[1].grid(True)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 5. Conclusion
# * **Prediction performance:** the GRU usually gives lower RMSE/MAE and higher R2 than the plain RNN.
# * **Convergence:** gates let gradients flow across the 30 time-steps, so the GRU reaches low loss in fewer epochs.
# * **Computational cost:** a GRU has about 3x the parameters of a SimpleRNN (three weight sets instead of one),
#   so each epoch is somewhat slower - the price paid for better learning of temporal dependencies.
# * **Why GRU helps:** the **update gate** decides how much past information to carry forward, and the **reset gate**
#   decides how much of it to ignore; together they reduce the vanishing-gradient problem of the simple RNN.
# * Results vary with the random seed and ticker; the model still cannot account for news or market shocks.
