import os, sys, threading

def setup_background():
    """Run data pipeline in background after server starts."""
    import time
    time.sleep(5)  # wait for server to be ready

    print("=== Background setup starting ===")
    sys.path.insert(0, ".")

    try:
        from backend.utils.database import init_db
        init_db()

        from backend.data_pipeline.fetch_prices import run_all as fetch_prices
        from backend.data_pipeline.fetch_fundamentals import run_all as fetch_fundamentals
        from backend.data_pipeline.compute_indicators import run_all as compute_indicators
        from backend.models.features import build_feature_matrix
        from backend.models.train import run_training
        import pandas as pd

        fetch_prices()
        fetch_fundamentals()
        compute_indicators()
        df = build_feature_matrix()
        os.makedirs("data/processed", exist_ok=True)
        df.to_csv("data/processed/feature_matrix.csv", index=False)
        run_training()
        print("=== Background setup complete ===")
    except Exception as e:
        print(f"=== Setup error: {e} ===")

def run_setup_if_needed():
    """Only run setup if models don't exist yet."""
    models_exist = (
        os.path.exists("backend/models/saved/model_5d.joblib") and
        os.path.exists("backend/models/saved/model_20d.joblib")
    )
    if not models_exist:
        print("Models not found — running setup in background...")
        t = threading.Thread(target=setup_background, daemon=True)
        t.start()
    else:
        print("Models found — skipping setup.")

run_setup_if_needed()