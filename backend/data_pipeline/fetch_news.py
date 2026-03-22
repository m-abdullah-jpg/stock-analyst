import sys, os, requests
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree
from email.utils import parsedate_to_datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.utils.database import SessionLocal, NewsHeadline, init_db
from backend.utils.config   import NEWS_API_KEY, TICKERS, TICKER_NAMES


def parse_date(pub_str: str):
    """Try multiple date formats used by RSS feeds. Returns None if unparseable."""
    if not pub_str:
        return None
    # RFC 2822 — standard RSS: "Thu, 20 Mar 2026 15:30:00 +0000"
    try:
        return parsedate_to_datetime(pub_str).replace(tzinfo=None)
    except:
        pass
    # ISO 8601 — NewsAPI: "2026-03-20T15:30:00Z"
    try:
        return datetime.strptime(pub_str, "%Y-%m-%dT%H:%M:%SZ")
    except:
        pass
    # ISO with offset: "2026-03-20T15:30:00+00:00"
    try:
        return datetime.fromisoformat(pub_str).replace(tzinfo=None)
    except:
        pass
    return None


def fetch_yahoo_rss(ticker: str) -> list[dict]:
    """Fetch headlines from Yahoo Finance RSS — free, no key needed."""
    urls = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        f"https://finance.yahoo.com/rss/headline?s={ticker}",
    ]
    headers = {"User-Agent": "Mozilla/5.0 (compatible; StockBot/1.0)"}

    for url in urls:
        try:
            resp = requests.get(url, timeout=10, headers=headers)
            if resp.status_code != 200:
                continue
            root     = ElementTree.fromstring(resp.content)
            articles = []
            for item in root.findall(".//item"):
                title   = item.findtext("title", "").strip()
                pub_str = item.findtext("pubDate", "")
                if not title or title == "[Removed]":
                    continue
                pub_dt = parse_date(pub_str)
                if pub_dt is None:
                    continue          # skip articles with no parseable date
                articles.append({
                    "headline":     title,
                    "source":       "Yahoo Finance",
                    "published_at": pub_dt,
                })
            if articles:
                return articles
        except:
            continue
    return []


def fetch_google_news_rss(ticker: str) -> list[dict]:
    """Google News RSS — free, no key, very reliable."""
    company = TICKER_NAMES.get(ticker, ticker)
    query   = f"{company} stock".replace(" ", "+")
    url     = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; StockBot/1.0)"}
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.status_code != 200:
            return []
        root     = ElementTree.fromstring(resp.content)
        articles = []
        for item in root.findall(".//item"):
            title   = item.findtext("title", "").strip()
            pub_str = item.findtext("pubDate", "")
            if not title:
                continue
            pub_dt = parse_date(pub_str)
            if pub_dt is None:
                continue              # skip articles with no parseable date
            articles.append({
                "headline":     title,
                "source":       "Google News",
                "published_at": pub_dt,
            })
        return articles
    except:
        return []


def fetch_newsapi(ticker: str, days_back: int = 25) -> list[dict]:
    """Fetch from NewsAPI (requires key, free plan limited to 25 days)."""
    if not NEWS_API_KEY:
        return []
    try:
        from newsapi import NewsApiClient
        client    = NewsApiClient(api_key=NEWS_API_KEY)
        company   = TICKER_NAMES.get(ticker, ticker)
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        response  = client.get_everything(
            q=f'"{company}" OR "{ticker}" stock',
            from_param=from_date,
            language="en",
            sort_by="publishedAt",
            page_size=50,
        )
        articles = []
        for a in response.get("articles", []):
            title = a.get("title", "").strip()
            if not title or title == "[Removed]":
                continue
            pub_dt = parse_date(a.get("publishedAt", ""))
            if pub_dt is None:
                continue              # skip articles with no parseable date
            articles.append({
                "headline":     title,
                "source":       a.get("source", {}).get("name", "NewsAPI"),
                "published_at": pub_dt,
            })
        return articles
    except Exception as e:
        print(f"    NewsAPI error for {ticker}: {e}")
        return []


def store_articles(ticker: str, articles: list[dict]) -> int:
    """Store articles in DB, skip duplicates. Returns count inserted."""
    inserted = 0
    with SessionLocal() as session:
        for a in articles:
            exists = session.query(NewsHeadline).filter_by(
                ticker=ticker, headline=a["headline"]
            ).first()
            if exists:
                continue
            session.add(NewsHeadline(
                ticker       = ticker,
                headline     = a["headline"],
                source       = a["source"],
                published_at = a["published_at"],
            ))
            inserted += 1
        session.commit()
    return inserted


def fetch_news_for_ticker(ticker: str, days_back: int = 25) -> int:
    """Fetch from all sources and store. Returns total new rows inserted."""
    articles = []
    articles.extend(fetch_yahoo_rss(ticker))
    articles.extend(fetch_google_news_rss(ticker))
    if NEWS_API_KEY:
        articles.extend(fetch_newsapi(ticker, days_back=min(days_back, 25)))
    return store_articles(ticker, articles)


def run_all():
    init_db()
    print(f"Fetching news for {len(TICKERS)} tickers (Yahoo RSS + Google News + NewsAPI)...")
    total = 0
    for ticker in TICKERS:
        print(f"  {ticker}...", end=" ")
        n = fetch_news_for_ticker(ticker)
        print(f"{n} new headlines.")
        total += n
    print(f"\nDone. Total new headlines: {total}")


if __name__ == "__main__":
    run_all()
