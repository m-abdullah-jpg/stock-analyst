import sys, os
from fastapi import APIRouter, HTTPException
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.api.schemas             import (PredictionResponse, SentimentResponse,
                                              TopPicksResponse, TopPicksItem, HealthResponse)
from backend.models.predict          import predict_ticker, load_models
from backend.models.sentiment_signal import get_current_sentiment
from backend.utils.config            import TICKERS

router = APIRouter()

# Load models once at module import — not on every request
_models = None

def get_models():
    global _models
    if _models is None:
        _models = load_models()
    return _models

# ─── Health check ────────────────────────────────────────────────────
@router.get("/health", response_model=HealthResponse)
def health():
    try:
        m5, m20 = get_models()
        loaded  = True
    except:
        loaded  = False
    return HealthResponse(
        status       = "ok",
        models_loaded= loaded,
        tickers      = TICKERS,
    )

# ─── Single stock prediction ─────────────────────────────────────────
@router.get("/analyze/{ticker}", response_model=PredictionResponse)
def analyze(ticker: str):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(
            status_code=404,
            detail=f"{ticker} not in watchlist. Available: {TICKERS}"
        )
    try:
        m5, m20 = get_models()
        result  = predict_ticker(ticker, m5, m20)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return PredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Sentiment for one ticker ─────────────────────────────────────────
@router.get("/sentiment/{ticker}", response_model=SentimentResponse)
def sentiment(ticker: str):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail=f"{ticker} not in watchlist.")
    result = get_current_sentiment(ticker)
    return SentimentResponse(**result)

# ─── Top picks ────────────────────────────────────────────────────────
@router.get("/picks", response_model=TopPicksResponse)
def top_picks(limit: int = 5):
    m5, m20 = get_models()
    picks   = []

    for ticker in TICKERS:
        try:
            p = predict_ticker(ticker, m5, m20)
            if "error" in p:
                continue

            # Composite score: weight confidence + sentiment
            conf_score  = p["confidence_5d"] / 100
            sent_score  = (p.get("sentiment_score", 0) + 1) / 2  # normalize -1..1 → 0..1
            buy_bonus   = 0.1 if "Buy" in p["signal_5d"] else 0.0
            composite   = (conf_score * 0.6) + (sent_score * 0.3) + buy_bonus

            picks.append(TopPicksItem(
                ticker         = p["ticker"],
                close          = p["close"],
                signal_5d      = p["signal_5d"],
                confidence_5d  = p["confidence_5d"],
                signal_20d     = p["signal_20d"],
                confidence_20d = p["confidence_20d"],
                sentiment      = p["sentiment"],
                rsi            = p["rsi"],
                score          = round(composite, 4),
            ))
        except:
            continue

    picks.sort(key=lambda x: x.score, reverse=True)
    return TopPicksResponse(
        picks     = picks[:limit],
        generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

# ─── All tickers summary ──────────────────────────────────────────────
@router.get("/summary")
def summary():
    m5, m20 = get_models()
    results = []
    for ticker in TICKERS:
        try:
            p = predict_ticker(ticker, m5, m20)
            if "error" not in p:
                results.append(p)
        except:
            continue
    return {"tickers": results, "count": len(results)}