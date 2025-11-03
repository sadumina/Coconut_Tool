# app/main.py
from __future__ import annotations
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool   # ✅ allows sync Playwright inside async FastAPI
from datetime import datetime
from typing import Optional, List, Dict, Any
from .config import settings
from .db import get_db, get_client
from .scraper.icc_scraper import scrape_icc
from .services.aggregator import basic_stats, month_averages, mom_change, compare_periods

import sys
import asyncio

# ✅ FIX: Required for Playwright on Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = FastAPI(
    title="Coconut Shell Charcoal API",
    version="1.0.0",
)

# -------------------------------------------------------
# ✅ Enable CORS (for frontend)
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# ✅ Test DB connection on startup
# -------------------------------------------------------
@app.on_event("startup")
async def startup_db_connection():
    try:
        client = await get_client()
        await client.admin.command("ping")
        print("✅ MongoDB connected!")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)


@app.get("/health")
async def health():
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()}


# -------------------------------------------------------
# ✅ SCRAPE + SAVE TO DB
# -------------------------------------------------------
from starlette.concurrency import run_in_threadpool

@app.post("/scrape")
async def scrape_and_save(db=Depends(get_db)):
    rows = await run_in_threadpool(scrape_icc)   # run the sync selenium scraper

    if not rows:
        return {"saved": 0, "skipped": 0, "total": 0, "note": "No rows extracted (site blocked or charcoal not listed)"}

    saved = skipped = 0
    for row in rows:
        result = await db["prices"].update_one(
            {"date": row["date"], "market": row["market"], "product": row["product"]},
            {"$setOnInsert": row},
            upsert=True
        )
        if getattr(result, "upserted_id", None):
            saved += 1
        else:
            skipped += 1

    return {"saved": saved, "skipped": skipped, "total": len(rows)}



# -------------------------------------------------------
# ✅ Get markets list
# -------------------------------------------------------
@app.get("/markets")
async def list_markets(db=Depends(get_db)):
    return sorted(await db["prices"].distinct("market"))


# -------------------------------------------------------
# ✅ Get saved prices
# -------------------------------------------------------
@app.get("/prices")
async def get_prices(
    market: Optional[str] = Query(default=None),
    db=Depends(get_db)
):
    query = {"product": "Coconut Shell Charcoal"}
    if market:
        query["market"] = market

    cursor = db["prices"].find(query, projection={"_id": 0}).sort("date", 1)
    return [doc async for doc in cursor]


# -------------------------------------------------------
# ✅ Aggregated Stats
# -------------------------------------------------------
@app.get("/stats")
async def get_stats(markets: Optional[List[str]] = Query(default=None), db=Depends(get_db)):
    query = {"product": "Coconut Shell Charcoal"}
    if markets:
        query["market"] = {"$in": markets}

    cursor = db["prices"].find(query)
    items = [doc async for doc in cursor]

    grouped = {}
    for rec in items:
        grouped.setdefault(rec["market"], []).append(rec)

    return {
        market: {
            "stats": basic_stats(rows),
            "monthly_avg": month_averages(rows),
            "mom": mom_change(month_averages(rows)),
        }
        for market, rows in grouped.items()
    }


# -------------------------------------------------------
# ✅ Month-over-month trend
# -------------------------------------------------------
@app.get("/mom")
async def get_mom(markets: Optional[List[str]] = Query(default=None), db=Depends(get_db)):
    query = {"product": "Coconut Shell Charcoal"}
    if markets:
        query["market"] = {"$in": markets}

    cursor = db["prices"].find(query).sort("date", 1)
    grouped = {}

    async for rec in cursor:
        grouped.setdefault(rec["market"], []).append(rec)

    return {m: mom_change(month_averages(r)) for m, r in grouped.items()}


# -------------------------------------------------------
# ✅ Compare A vs B date range
# -------------------------------------------------------
@app.get("/compare")
async def compare(
    startA: datetime, endA: datetime,
    startB: datetime, endB: datetime,
    markets: Optional[List[str]] = Query(default=None),
    db=Depends(get_db)
):
    query = {"product": "Coconut Shell Charcoal"}
    if markets:
        query["market"] = {"$in": markets}

    cursor = db["prices"].find(query).sort("date", 1)
    grouped = {}

    async for rec in cursor:
        grouped.setdefault(rec["market"], []).append(rec)

    return {m: compare_periods(r, startA, endA, startB, endB) for m, r in grouped.items()}
