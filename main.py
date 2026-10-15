import os
import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGIN = "https://dash-ssatqk.example.com"
EMAIL = os.environ.get("EMAIL", "your-email@example.com")

app = FastAPI(title="Stats API")

# CORS: exactly one allowed origin, never "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


# Added AFTER CORS so it is the outermost layer and tags every response,
# including preflight responses and rejected preflights.
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


@app.get("/stats")
def stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values provided")
    total = sum(nums)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": round(total / len(nums), 6),
    }


@app.get("/")
def root():
    return {"status": "ok"}
