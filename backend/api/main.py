import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Run background setup if models missing
import startup

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title       = "Stock Analyst API",
    description = "AI-powered stock predictions using XGBoost + FinBERT",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
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
```

**Step 3 — update Procfile to just start the server directly**
```
web: uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT