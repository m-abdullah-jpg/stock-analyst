import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title       = "Stock Analyst API",
    description = "AI-powered stock predictions using XGBoost + FinBERT",
    version     = "1.0.0",
)

# CORS — allows the React frontend (localhost:5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["http://localhost:5173", "http://localhost:3000", "*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "Stock Analyst API",
        "docs":    "/docs",
        "health":  "/api/v1/health",
    }