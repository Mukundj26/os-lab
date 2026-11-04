# %% [markdown]
# # Practical 10: Stock Market Time-Series Forecasting using RNN - CO1, CO2, CO5
# **Aim:** Download stock data from Yahoo Finance, visualize trends, scale with Min-Max, create 30-day windows,
# and predict the next day's closing price with an RNN (50 units) + Dense output.
#
# Install once: `pip install yfinance`

# %%
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
tf.keras.utils.set_random_seed(SEED)
TICKER = "AAPL"                  # change to any ticker, e.g. "TCS.NS", "RELIANCE.NS", "^NSEI"
START, END = "2015-01-01", "2025-01-01"
WINDOW = 30
FEATURES = ["Open", "High", "Low", "Close", "Volume"]

# %% [markdown]
# ## 1. Download data
# If the download fails (no internet), put a CSV named `stock.csv` with columns Date, Open, High, Low, Close, Volume
# in the same folder and it will be used instead.

# %%
try:
    df = yf.download(TICKER, start=START, end=END, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):          # newer yfinance returns multi-level columns
        df.columns = df.columns.get_level_values(0)
    df = df[FEATURES].dropna()
    assert len(df) > 100
except Exception as e:
    print("Yahoo Finance download failed:", e, "-> reading stock.csv")
    df = pd.read_csv("stock.csv", parse_dates=["Date"], index_col="Date")[FEATURES].dropna()

print(df.shape)
df.head()

# %% [markdown]
# ## 2. Visualize trends

# %%
fig, ax = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
ax[0].plot(df.index, df["Close"], label="Close")
ax[0].plot(df["Close"].rolling(50).mean(), label="50-day MA")
ax[0].plot(df["Close"].rolling(200).mean(), label="200-day MA")
ax[0].set_title(f"{TICKER} closing price"); ax[0].legend(); ax[0].grid(True)
ax[1].bar(df.index, df["Volume"], width=1.0, color="gray"); ax[1].set_title("Volume")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 3. Min-Max scaling and 30-day sliding windows
# The scaler is fitted on the **training period only** to avoid data leakage. The split is chronological.

# %%
split = int(len(df) * 0.8)
scaler = MinMaxScaler().fit(df.iloc[:split])
scaled = scaler.transform(df)
close_idx = FEATURES.index("Close")

def make_windows(data, window=WINDOW):
    X, y = [], []
    for i in range(window, len(data)):
        X.append(data[i - window:i])            # previous 30 days, all 5 features
        y.append(data[i, close_idx])            # next day's closing price
    return np.array(X), np.array(y)

X_all, y_all = make_windows(scaled)
cut = split - WINDOW
X_train, y_train = X_all[:cut], y_all[:cut]
X_test, y_test = X_all[cut:], y_all[cut:]
print("X_train", X_train.shape, "X_test", X_test.shape)

def inverse_close(values):
    """Convert scaled close values back to price."""
    dummy = np.zeros((len(values), len(FEATURES)))
    dummy[:, close_idx] = np.ravel(values)
    return scaler.inverse_transform(dummy)[:, close_idx]

# %% [markdown]
# ## 4. RNN model (SimpleRNN with 50 hidden units + Dense output)

# %%
model = keras.Sequential([
    layers.Input(shape=(WINDOW, len(FEATURES))),
    layers.SimpleRNN(50),
    layers.Dense(1),
])
model.compile(optimizer=keras.optimizers.Adam(0.001), loss="mse")
model.summary()

history = model.fit(X_train, y_train, epochs=30, batch_size=32, validation_split=0.1, verbose=1,
                    callbacks=[keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)])

# %% [markdown]
# ## 5. Training and validation loss

# %%
plt.figure(figsize=(8, 4))
plt.plot(history.history["loss"], label="Training loss")
plt.plot(history.history["val_loss"], label="Validation loss")
plt.xlabel("Epoch"); plt.ylabel("MSE (scaled)"); plt.title("RNN loss curves"); plt.legend(); plt.grid(True)
plt.show()

# %% [markdown]
# ## 6. Prediction performance

# %%
pred = inverse_close(model.predict(X_test, verbose=0))
actual = inverse_close(y_test)

rmse = np.sqrt(mean_squared_error(actual, pred))
mae = mean_absolute_error(actual, pred)
mape = np.mean(np.abs((actual - pred) / actual)) * 100
r2 = r2_score(actual, pred)
print(f"RMSE: {rmse:.3f} | MAE: {mae:.3f} | MAPE: {mape:.2f}% | R2: {r2:.4f}")

dates = df.index[split:]
plt.figure(figsize=(13, 5))
plt.plot(dates, actual, label="Actual close")
plt.plot(dates, pred, label="RNN predicted close")
plt.title(f"{TICKER}: actual vs predicted (test period)"); plt.xlabel("Date"); plt.ylabel("Price")
plt.legend(); plt.grid(True); plt.show()

# %% [markdown]
# ## 7. Conclusion and limitations
# * The RNN follows the overall trend well because each prediction uses a 30-day window of past prices.
# * Predictions lag behind sharp moves: the model largely learns "tomorrow is close to today".
# * SimpleRNNs suffer from **vanishing gradients** on long sequences, so they remember short-term patterns only
#   (the motivation for GRU/LSTM in Practical 11).
# * Prices depend on news, earnings and market sentiment that are **not** in OHLCV data, so this is not
#   reliable for real trading decisions. Used here for learning purposes only.
