# backend/utils/config.py
# Central place to load all config and API keys

import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file from project root

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# Tickers we track across the whole project
TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "META", "TSLA", "JPM", "LLY", "V"
]

TICKER_NAMES = {
    "AAPL": "Apple",       "MSFT": "Microsoft",
    "NVDA": "NVIDIA",      "GOOGL": "Google Alphabet",
    "AMZN": "Amazon",      "META": "Meta",
    "TSLA": "Tesla",       "JPM": "JPMorgan",
    "LLY":  "Eli Lilly",   "V":    "Visa",
}