import yfinance as yf
from datetime import datetime
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.database import SessionLocal, StockFundamentals, init_db

TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "META", "TSLA", "JPM", "LLY", "V"
]

def safe_get(info: dict, key: str, default=None):
    """Get a value, return default if missing or None."""
    val = info.get(key, default)
    return val if val is not None else default

def fetch_fundamentals(ticker: str) -> bool:
    print(f"  {ticker}...", end=" ")
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        fundamentals = {
            "ticker":         ticker,
            "name":           safe_get(info, "longName", ticker),
            "sector":         safe_get(info, "sector", "Unknown"),
            "market_cap":     safe_get(info, "marketCap"),
            "pe_ratio":       safe_get(info, "trailingPE"),
            "forward_pe":     safe_get(info, "forwardPE"),
            "eps":            safe_get(info, "trailingEps"),
            "revenue_growth": safe_get(info, "revenueGrowth"),
            "profit_margin":  safe_get(info, "profitMargins"),
            "debt_to_equity": safe_get(info, "debtToEquity"),
            "updated_at":     datetime.utcnow(),
        }

        with SessionLocal() as session:
            existing = session.query(StockFundamentals).filter_by(
                ticker=ticker
            ).first()

            if existing:
                for k, v in fundamentals.items():
                    setattr(existing, k, v)
                print("updated.")
            else:
                session.add(StockFundamentals(**fundamentals))
                print("inserted.")

            session.commit()
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def run_all():
    init_db()
    print(f"Fetching fundamentals for {len(TICKERS)} tickers...")
    for ticker in TICKERS:
        fetch_fundamentals(ticker)
    print("Done.")

if __name__ == "__main__":
    run_all()