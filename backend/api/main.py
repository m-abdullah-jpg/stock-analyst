import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.api.routes import router
import threading

def run_background_setup():
    """Run data pipeline in a background thread."""
    try:
        from backend.utils.database import init_db
        init_db()
        from backend.data_pipeline.fetch_prices       import run_all as fetch_prices
        from backend.data_pipeline.fetch_fundamentals import run_all as fetch_fundamentals
        from backend.data_pipeline.compute_indicators import run_all as compute_indicators
        from backend.models.features                  import build_feature_matrix
        from backend.models.train                     import run_training
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs AFTER server is already listening on $PORT
    models_exist = (
        os.path.exists("backend/models/saved/model_5d.joblib") and
        os.path.exists("backend/models/saved/model_20d.joblib")
    )
    if not models_exist:
        print("Models not found — starting background setup...")
        t = threading.Thread(target=run_background_setup, daemon=True)
        t.start()
    yield

app = FastAPI(
    title       = "Stock Analyst API",
    description = "AI-powered stock predictions using XGBoost + FinBERT",
    version     = "1.0.0",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Stock Analyst API", "docs": "/docs", "health": "/api/v1/health"}