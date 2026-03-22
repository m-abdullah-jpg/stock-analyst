import sys, os
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.models.features import build_feature_matrix, FEATURE_COLS

MODEL_DIR = "backend/models/saved"

def walk_forward_validate(df, feature_cols, target_col="target_5d", n_splits=5):
    df = df.sort_values("date").dropna(subset=feature_cols+[target_col])
    dates     = sorted(df["date"].unique())
    fold_size = len(dates) // (n_splits + 1)
    results   = []
    print(f"  Walk-forward validation ({n_splits} folds)...")
    for i in range(1, n_splits+1):
        cutoff   = dates[fold_size * i]
        train_df = df[df["date"] <  cutoff]
        test_df  = df[df["date"] >= cutoff]
        if i < n_splits:
            next_cut = dates[min(fold_size*(i+1), len(dates)-1)]
            test_df  = test_df[test_df["date"] < next_cut]
        if len(train_df) < 100 or len(test_df) < 20:
            continue
        model = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05,
                              subsample=0.8, colsample_bytree=0.8,
                              eval_metric="logloss", random_state=42, verbosity=0)
        model.fit(train_df[feature_cols].fillna(0), train_df[target_col])
        preds = model.predict(test_df[feature_cols].fillna(0))
        acc   = accuracy_score(test_df[target_col], preds)
        results.append(acc)
        print(f"    Fold {i}: train={len(train_df)} test={len(test_df)} acc={acc:.3f}")
    mean_acc = np.mean(results)
    baseline = df[target_col].mean()
    print(f"  Mean accuracy: {mean_acc:.3f}  (random baseline: {baseline:.3f})")
    return mean_acc

def train_final_model(df, feature_cols, target_col="target_5d"):
    df_clean = df.dropna(subset=feature_cols+[target_col])
    model = XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8,
                          eval_metric="logloss", random_state=42, verbosity=0)
    model.fit(df_clean[feature_cols].fillna(0), df_clean[target_col])
    print(f"  Trained on {len(df_clean)} rows, {len(feature_cols)} features.")
    return model

def run_training():
    os.makedirs(MODEL_DIR, exist_ok=True)
    matrix_path = "data/processed/feature_matrix.csv"
    if os.path.exists(matrix_path):
        df = pd.read_csv(matrix_path, parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"]).dt.date
    else:
        print("Building feature matrix first...")
        df = build_feature_matrix()

    print("\n=== 5-day model ===")
    walk_forward_validate(df, FEATURE_COLS, "target_5d")
    m5 = train_final_model(df, FEATURE_COLS, "target_5d")
    joblib.dump(m5, f"{MODEL_DIR}/model_5d.joblib")

    print("\n=== 20-day model ===")
    walk_forward_validate(df, FEATURE_COLS, "target_20d")
    m20 = train_final_model(df, FEATURE_COLS, "target_20d")
    joblib.dump(m20, f"{MODEL_DIR}/model_20d.joblib")

    print("\n=== Top 10 features (5-day model) ===")
    fi = pd.DataFrame({"feature": FEATURE_COLS, "importance": m5.feature_importances_})
    fi = fi.sort_values("importance", ascending=False)
    for _, r in fi.head(10).iterrows():
        bar = "█" * int(r["importance"] * 200)
        print(f"  {r['feature']:25} {r['importance']:.4f}  {bar}")
    fi.to_csv(f"{MODEL_DIR}/feature_importance.csv", index=False)
    print(f"\nModels saved to {MODEL_DIR}/")
    return m5, m20

if __name__ == "__main__":
    run_training()