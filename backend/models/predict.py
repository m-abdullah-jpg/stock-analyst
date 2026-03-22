import sys, os
import pandas as pd
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.models.features         import load_indicators, load_sentiment,                                             load_fundamentals, FEATURE_COLS
from backend.models.sentiment_signal import get_current_sentiment
from backend.utils.config            import TICKERS

MODEL_DIR = "backend/models/saved"

def load_models():
    m5  = joblib.load(f"{MODEL_DIR}/model_5d.joblib")
    m20 = joblib.load(f"{MODEL_DIR}/model_20d.joblib")
    return m5, m20

def build_latest_features(ticker):
    ind  = load_indicators(ticker)
    sent = load_sentiment(ticker)
    fund = load_fundamentals(ticker)
    if ind.empty:
        return None
    latest = ind.sort_values("date").iloc[-1].copy()
    if not sent.empty:
        s = sent.sort_values("date").iloc[-1]
        latest["sentiment_score"] = s.get("sentiment_score", 0.0)
        latest["sentiment_pos"]   = s.get("sentiment_pos",   0.0)
        latest["sentiment_neg"]   = s.get("sentiment_neg",   0.0)
        latest["sent_momentum"]   = s.get("sent_momentum",   0.0)
    else:
        latest["sentiment_score"] = 0.0
        latest["sentiment_pos"]   = 0.0
        latest["sentiment_neg"]   = 0.0
        latest["sent_momentum"]   = 0.0
    for k, v in fund.items():
        latest[k] = v
    return latest

def signal_label(pred, conf):
    if pred == 1 and conf > 0.60: return "Strong Buy"
    if pred == 1 and conf > 0.52: return "Buy"
    if pred == 0 and conf > 0.60: return "Strong Sell"
    if pred == 0 and conf > 0.52: return "Sell"
    return "Hold"

def predict_ticker(ticker, m5, m20):
    f = build_latest_features(ticker)
    if f is None:
        return {"ticker": ticker, "error": "no data"}
    X        = pd.DataFrame([f[FEATURE_COLS].fillna(0)])
    prob_5d  = m5.predict_proba(X)[0]
    prob_20d = m20.predict_proba(X)[0]
    sent     = get_current_sentiment(ticker)
    return {
        "ticker":          ticker,
        "date":            str(f["date"]),                          # ← add this
        "close":           round(float(f["close"]), 2),
        "signal_5d":       signal_label(int(m5.predict(X)[0]),  float(max(prob_5d))),
        "confidence_5d":   round(float(max(prob_5d))  * 100, 1),
        "signal_20d":      signal_label(int(m20.predict(X)[0]), float(max(prob_20d))),
        "confidence_20d":  round(float(max(prob_20d)) * 100, 1),
        "sentiment":       sent["label"],
        "sentiment_score": sent["score"],                           # ← add this
        "rsi":             round(float(f.get("rsi", 0)), 1),
        "macd":            round(float(f.get("macd", 0)), 4),      # ← add this
        "pe_ratio":        float(f.get("pe_ratio", 0)) or None,
        "forward_pe":      float(f.get("forward_pe", 0)) or None,
    }

def run_predictions():
    m5, m20 = load_models()
    print(f"\n{'Ticker':<7}{'Close':>8}  {'5d':^13}{'Conf':>6}  {'20d':^13}{'Conf':>6}  {'Sent':<10}{'RSI':>5}")
    print("-" * 72)
    for ticker in TICKERS:
        p = predict_ticker(ticker, m5, m20)
        if "error" in p:
            continue
        print(f"{p['ticker']:<7}{p['close']:>8.2f}  {p['signal_5d']:^13}{p['confidence_5d']:>5.1f}%  {p['signal_20d']:^13}{p['confidence_20d']:>5.1f}%  {p['sentiment']:<10}{p['rsi']:>5.1f}")

if __name__ == "__main__":
    run_predictions()
