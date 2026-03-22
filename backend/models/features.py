import sys, os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.database import SessionLocal, StockFundamentals, NewsHeadline
from backend.utils.config   import TICKERS

PROCESSED_DIR = "data/processed"

def load_indicators(ticker):
    path = os.path.join(PROCESSED_DIR, f"{ticker}_indicators.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

def load_sentiment(ticker):
    with SessionLocal() as session:
        rows = session.query(NewsHeadline).filter(
            NewsHeadline.ticker    == ticker,
            NewsHeadline.sentiment != None,
        ).all()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([{"date": r.published_at.date(), "sentiment": r.sentiment} for r in rows])
    daily = df.groupby("date").agg(
        sentiment_score=("sentiment","mean"),
        sentiment_count=("sentiment","count"),
        sentiment_pos  =("sentiment", lambda x: (x>0.15).mean()),
        sentiment_neg  =("sentiment", lambda x: (x<-0.15).mean()),
    ).reset_index()
    daily["sent_3d"]       = daily["sentiment_score"].rolling(3, min_periods=1).mean()
    daily["sent_7d"]       = daily["sentiment_score"].rolling(7, min_periods=1).mean()
    daily["sent_momentum"] = daily["sent_3d"] - daily["sent_7d"]
    return daily

def load_fundamentals(ticker):
    with SessionLocal() as session:
        f = session.query(StockFundamentals).filter_by(ticker=ticker).first()
    if not f:
        return {}
    return {
        "pe_ratio":       f.pe_ratio       or 0.0,
        "forward_pe":     f.forward_pe     or 0.0,
        "eps":            f.eps            or 0.0,
        "revenue_growth": f.revenue_growth or 0.0,
        "profit_margin":  f.profit_margin  or 0.0,
        "debt_to_equity": f.debt_to_equity or 0.0,
    }

def make_target(df, horizon=5):
    df = df.copy().sort_values("date").reset_index(drop=True)
    future        = df["close"].shift(-horizon)
    df["target_5d"]  = (df["close"].shift(-5)  > df["close"]).astype(float)
    df["target_20d"] = (df["close"].shift(-20) > df["close"]).astype(float)
    df["return_5d"]  = (df["close"].shift(-5)  - df["close"]) / df["close"]
    df["return_20d"] = (df["close"].shift(-20) - df["close"]) / df["close"]
    return df

def build_feature_matrix(tickers=None):
    if tickers is None:
        tickers = TICKERS
    all_dfs = []
    for ticker in tickers:
        print(f"  {ticker}...", end=" ")
        ind = load_indicators(ticker)
        if ind.empty:
            print("no data, skipping.")
            continue
        sent = load_sentiment(ticker)
        fund = load_fundamentals(ticker)
        if not sent.empty:
            sent["date"] = pd.to_datetime(sent["date"]).dt.date
            df = ind.merge(sent, on="date", how="left")
            for c in ["sentiment_score","sentiment_count","sentiment_pos","sentiment_neg","sent_momentum"]:
                df[c] = df[c].ffill().fillna(0)
        else:
            df = ind.copy()
            for c in ["sentiment_score","sentiment_count","sentiment_pos","sentiment_neg","sent_momentum"]:
                df[c] = 0.0
        for k, v in fund.items():
            df[k] = v
        df = make_target(df)
        df["ticker"] = ticker
        all_dfs.append(df)
        print(f"{len(df)} rows.")
    if not all_dfs:
        return pd.DataFrame()
    out = pd.concat(all_dfs, ignore_index=True)
    print(f"\nTotal: {len(out)} rows x {len(out.columns)} columns")
    return out

FEATURE_COLS = [
    # Technical — trend
    "sma_20", "sma_50", "sma_200", "ema_12", "ema_26",
    # Technical — momentum
    "macd", "macd_signal", "macd_hist",
    # Technical — volatility
    "bb_upper", "bb_lower", "bb_pct",
    # Technical — volume
    "vol_ratio",
    # Price momentum
    "ret_1d", "ret_5d", "ret_20d",
    # Sentiment
    "sentiment_score", "sentiment_pos", "sentiment_neg", "sent_momentum",
    # Fundamentals
    "pe_ratio", "forward_pe", "eps", "revenue_growth",
    "profit_margin", "debt_to_equity",
]

if __name__ == "__main__":
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("Building feature matrix...")
    df = build_feature_matrix()
    if not df.empty:
        out = os.path.join(PROCESSED_DIR, "feature_matrix.csv")
        df.to_csv(out, index=False)
        print(f"Saved to {out}")
        print("\nTarget distribution (5-day):")
        print(df["target_5d"].value_counts(normalize=True).round(3))
