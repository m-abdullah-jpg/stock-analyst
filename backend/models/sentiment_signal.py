import sys, os
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.database import SessionLocal, NewsHeadline
from backend.utils.config   import TICKERS

def get_daily_sentiment(ticker: str, days: int = 30) -> pd.DataFrame:
    """
    Aggregate headline sentiment into a daily signal for one ticker.
    Returns a DataFrame with columns: date, avg_score, headline_count,
    positive_pct, negative_pct, sentiment_momentum.
    """
    from datetime import timezone
    since = datetime.now(timezone.utc) - timedelta(days=days)

    with SessionLocal() as session:
        rows = session.query(NewsHeadline).filter(
            NewsHeadline.ticker      == ticker,
            NewsHeadline.published_at >= since,
            NewsHeadline.sentiment   != None,
        ).all()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame([{
        "date":      row.published_at.date(),
        "sentiment": row.sentiment,
        "headline":  row.headline,
    } for row in rows])

    # Daily aggregation
    daily = df.groupby("date").agg(
        avg_score      = ("sentiment", "mean"),
        headline_count = ("sentiment", "count"),
        positive_pct   = ("sentiment", lambda x: (x > 0.15).mean()),
        negative_pct   = ("sentiment", lambda x: (x < -0.15).mean()),
    ).reset_index()

    daily = daily.sort_values("date")

    # Sentiment momentum: 3-day rolling mean minus 7-day rolling mean
    daily["sentiment_3d"]  = daily["avg_score"].rolling(3,  min_periods=1).mean()
    daily["sentiment_7d"]  = daily["avg_score"].rolling(7,  min_periods=1).mean()
    daily["sent_momentum"] = daily["sentiment_3d"] - daily["sentiment_7d"]

    daily["ticker"] = ticker
    return daily.round(4)

def get_current_sentiment(ticker: str) -> dict:
    """
    Get today's sentiment snapshot for a ticker.
    Returns a dict suitable for display or feature injection.
    """
    df = get_daily_sentiment(ticker, days=14)
    if df.empty:
        return {"ticker": ticker, "score": 0.0, "label": "neutral",
                "count": 0, "momentum": 0.0}

    latest = df.iloc[-1]
    score  = latest["avg_score"]
    label  = "bullish" if score > 0.1 else "bearish" if score < -0.1 else "neutral"

    return {
        "ticker":   ticker,
        "date":     str(latest["date"]),
        "score":    round(float(score), 4),
        "label":    label,
        "count":    int(latest["headline_count"]),
        "pos_pct":  round(float(latest["positive_pct"]) * 100, 1),
        "neg_pct":  round(float(latest["negative_pct"]) * 100, 1),
        "momentum": round(float(latest["sent_momentum"]), 4),
    }

def print_sentiment_report():
    """Print a sentiment summary for all tickers."""
    print(f"\n{'Ticker':<8} {'Score':>7} {'Label':<10} {'Headlines':>10} {'Momentum':>10}")
    print("-" * 50)
    for ticker in TICKERS:
        s = get_current_sentiment(ticker)
        print(f"{s['ticker']:<8} {s['score']:>7.3f} {s['label']:<10} {s['count']:>10} {s['momentum']:>10.3f}")

if __name__ == "__main__":
    print_sentiment_report()
