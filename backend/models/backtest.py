import sys, os
import pandas as pd
import numpy as np
from xgboost import XGBClassifier

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.models.features import FEATURE_COLS

def backtest(df, feature_cols, target_col="target_5d",
             return_col="return_5d", train_pct=0.7):
    df     = df.sort_values("date").dropna(subset=feature_cols+[target_col, return_col])
    cut    = int(len(df) * train_pct)
    train  = df.iloc[:cut]
    test   = df.iloc[cut:].copy()
    model  = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05,
                           eval_metric="logloss", random_state=42, verbosity=0)
    model.fit(train[feature_cols].fillna(0), train[target_col])
    test["pred"]  = model.predict(test[feature_cols].fillna(0))
    test["conf"]  = model.predict_proba(test[feature_cols].fillna(0)).max(axis=1)
    test["strat"] = np.where((test["pred"]==1)&(test["conf"]>0.52), test[return_col], 0.0)
    strat_ret = (1 + test["strat"]).prod() - 1
    bh_ret    = (1 + test[return_col]).prod() - 1
    win_rate  = (test.loc[test["pred"]==1, return_col] > 0).mean()
    return {
        "strategy": round(strat_ret*100, 2),
        "buyhold":  round(bh_ret*100,    2),
        "trades":   int((test["pred"]==1).sum()),
        "win_pct":  round(win_rate*100,  1),
    }

def run_backtest():
    path = "data/processed/feature_matrix.csv"
    if not os.path.exists(path):
        print("Run features.py first."); return
    df = pd.read_csv(path, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"]).dt.date

    print(f"{'Ticker':<7}{'Strategy':>10}{'Buy&Hold':>10}{'Trades':>8}{'Win%':>7}")
    print("-" * 44)
    for ticker in df["ticker"].unique():
        t = df[df["ticker"]==ticker].copy()
        try:
            r = backtest(t, FEATURE_COLS)
            print(f"{ticker:<7}{r['strategy']:>9.1f}%{r['buyhold']:>9.1f}%{r['trades']:>8}{r['win_pct']:>6.1f}%")
        except Exception as e:
            print(f"{ticker:<7} ERROR: {e}")

if __name__ == "__main__":
    run_backtest()