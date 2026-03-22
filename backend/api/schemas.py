from pydantic import BaseModel
from typing import Optional
from datetime import date

class PredictionResponse(BaseModel):
    ticker:          str
    date:            str
    close:           float
    signal_5d:       str
    confidence_5d:   float
    signal_20d:      str
    confidence_20d:  float
    sentiment:       str
    sentiment_score: float
    rsi:             float
    macd:            float
    pe_ratio:        Optional[float] = None
    forward_pe:      Optional[float] = None

class SentimentResponse(BaseModel):
    ticker:   str
    date:     str
    score:    float
    label:    str
    count:    int
    pos_pct:  float
    neg_pct:  float
    momentum: float

class TopPicksItem(BaseModel):
    ticker:         str
    close:          float
    signal_5d:      str
    confidence_5d:  float
    signal_20d:     str
    confidence_20d: float
    sentiment:      str
    rsi:            float
    score:          float   # composite ranking score

class TopPicksResponse(BaseModel):
    picks:      list[TopPicksItem]
    generated:  str

class HealthResponse(BaseModel):
    status:      str
    models_loaded: bool
    tickers:     list[str]