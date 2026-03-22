from sqlalchemy import (
    create_engine, Column, String, Float,
    Integer, Date, DateTime, Text, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./data/stock_analyst.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class StockPrice(Base):
    """Daily OHLCV data for each ticker."""
    __tablename__ = "stock_prices"

    id        = Column(Integer, primary_key=True)
    ticker    = Column(String(10), nullable=False, index=True)
    date      = Column(Date, nullable=False)
    open      = Column(Float)
    high      = Column(Float)
    low       = Column(Float)
    close     = Column(Float)
    volume    = Column(Float)
    adj_close = Column(Float)

    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_ticker_date"),
    )

class StockFundamentals(Base):
    """Key financial metrics per ticker."""
    __tablename__ = "stock_fundamentals"

    id             = Column(Integer, primary_key=True)
    ticker         = Column(String(10), nullable=False, unique=True)
    name           = Column(String(100))
    sector         = Column(String(50))
    market_cap     = Column(Float)
    pe_ratio       = Column(Float)
    forward_pe     = Column(Float)
    eps            = Column(Float)
    revenue_growth = Column(Float)
    profit_margin  = Column(Float)
    debt_to_equity = Column(Float)
    updated_at     = Column(DateTime, default=datetime.utcnow)

class NewsHeadline(Base):
    """News headlines for sentiment analysis (Phase 2)."""
    __tablename__ = "news_headlines"

    id           = Column(Integer, primary_key=True)
    ticker       = Column(String(10), nullable=False, index=True)
    headline     = Column(Text, nullable=False)
    source       = Column(String(100))
    published_at = Column(DateTime)
    sentiment    = Column(Float)   # filled in Phase 2
    fetched_at   = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)
    print("Database initialized.")

if __name__ == "__main__":
    init_db()