import pandas as pd
import pandas_ta as ta
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.database import SessionLocal, StockPrice

TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "META", "TSLA", "JPM", "LLY", "V"
]

def load_prices(ticker: str) -> pd.DataFrame:
    """Load all stored prices for a ticker into a DataFrame."""
    with SessionLocal() as session:
        rows = (
            session.query(StockPrice)
            .filter_by(ticker=ticker)
            .order_by(StockPrice.date)
            .all()
        )
        return pd.DataFrame([{
            "date":   r.date,
            "open":   r.open,
            "high":   r.high,
            "low":    r.low,
            "close":  r.close,
            "volume": r.volume,
        } for r in rows])

def compute_indicators(ticker: str) -> pd.DataFrame:
    """Return a DataFrame with all indicators computed."""
    df = load_prices(ticker)
    if df.empty or len(df) < 50:
        print(f"  {ticker}: not enough data (need 50+ rows).")
        return pd.DataFrame()

    # Moving averages
    df["sma_20"]  = ta.sma(df["close"], length=20)
    df["sma_50"]  = ta.sma(df["close"], length=50)
    df["sma_200"] = ta.sma(df["close"], length=200)
    df["ema_12"]  = ta.ema(df["close"], length=12)
    df["ema_26"]  = ta.ema(df["close"], length=26)

    # Momentum
    df["rsi"] = ta.rsi(df["close"], length=14)

    # Momentum — MACD (auto-detect column names)
    macd_df   = ta.macd(df["close"], fast=12, slow=26, signal=9)
    macd_cols = macd_df.columns.tolist()
    macd_col  = [c for c in macd_cols if c.startswith("MACD_")][0]
    sig_col   = [c for c in macd_cols if c.startswith("MACDs")][0]
    hist_col  = [c for c in macd_cols if c.startswith("MACDh")][0]

    df["macd"]        = macd_df[macd_col]
    df["macd_signal"] = macd_df[sig_col]
    df["macd_hist"]   = macd_df[hist_col]
    
    # Volatility — Bollinger Bands (auto-detect column names)
    bb = ta.bbands(df["close"], length=20, std=2)

    # pandas-ta names columns differently across versions
    # detect upper/lower/mid dynamically
    bb_cols = bb.columns.tolist()
    upper_col = [c for c in bb_cols if c.startswith("BBU")][0]
    lower_col = [c for c in bb_cols if c.startswith("BBL")][0]
    mid_col   = [c for c in bb_cols if c.startswith("BBM")][0]

    df["bb_upper"] = bb[upper_col]
    df["bb_lower"] = bb[lower_col]
    df["bb_mid"]   = bb[mid_col]
    df["bb_pct"]   = (df["close"] - df["bb_lower"]) / (
                        df["bb_upper"] - df["bb_lower"] + 1e-9)
    # Volume
    df["vol_sma20"] = ta.sma(df["volume"], length=20)
    df["vol_ratio"] = df["volume"] / (df["vol_sma20"] + 1e-9)

    # Price momentum features
    df["ret_1d"]  = df["close"].pct_change(1)
    df["ret_5d"]  = df["close"].pct_change(5)
    df["ret_20d"] = df["close"].pct_change(20)

    df["ticker"] = ticker
    return df.dropna()

def run_all():
    print("Computing technical indicators...")
    for ticker in TICKERS:
        print(f"  {ticker}...", end=" ")
        df = compute_indicators(ticker)
        if not df.empty:
            out_path = f"data/processed/{ticker}_indicators.csv"
            df.to_csv(out_path, index=False)
            print(f"saved {len(df)} rows to {out_path}")

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    run_all()
    print("\nDone! Check data/processed/ for CSV files.")
