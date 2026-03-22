import yfinance as yf
import pandas as pd
from sqlalchemy.dialects.sqlite import insert
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.database import SessionLocal, StockPrice, init_db

TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "META", "TSLA", "JPM", "LLY", "V"
]

def fetch_and_store(ticker: str, period: str = "2y") -> int:
    """
    Fetch price history for one ticker and store in DB.
    Returns number of rows inserted.
    """
    print(f"  Fetching {ticker}...", end=" ")
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if df.empty:
            print("no data returned.")
            return 0

        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
        df["ticker"] = ticker
        df["date"] = pd.to_datetime(df["date"]).dt.date

        rows = df[["ticker","date","open","high","low","close","volume"]].to_dict("records")

        with SessionLocal() as session:
            stmt = insert(StockPrice).values(rows)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["ticker", "date"]
            )
            result = session.execute(stmt)
            session.commit()
            inserted = result.rowcount
            print(f"{len(rows)} rows fetched, {inserted} new.")
            return inserted

    except Exception as e:
        print(f"ERROR: {e}")
        return 0

def run_all():
    init_db()
    print(f"Fetching price data for {len(TICKERS)} tickers...")
    total = 0
    for ticker in TICKERS:
        total += fetch_and_store(ticker)
    print(f"\nDone. Total new rows inserted: {total}")

if __name__ == "__main__":
    run_all()
