from __future__ import annotations
import sys
import asyncio
import os

# -------------------------------------------------------
# ✅ MUST be set BEFORE importing Playwright & FastAPI
# -------------------------------------------------------
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Depends, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from datetime import datetime
from typing import Optional, List

from .config import settings
from .db import get_db, get_client
from .services.aggregator import basic_stats, month_averages, mom_change, compare_periods
from .scraper.icc_scraper import scrape_icc
from .pdf.pdf_parser import extract_prices_from_pdf


app = FastAPI(
    title="Coconut Data API",
    version="2.0.0"
)

# -------------------------------------------------------
# ✅ CORS for frontend
# -------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ✅ allow all (temporary)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# ✅ Test DB connection at startup
# -------------------------------------------------------
@app.on_event("startup")
async def startup_db_connection():
    try:
        client = await get_client()
        await client.admin.command("ping")
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)


@app.get("/health")
async def health():
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()}


# -------------------------------------------------------
# ✅ Scrape CoconutCommunity website → Save to MongoDB
# -------------------------------------------------------
@app.post("/scrape")
async def scrape_and_save(db=Depends(get_db)):
    rows = await run_in_threadpool(scrape_icc)

    if not rows:
        return {"status": "blocked_or_empty", "saved": 0, "skipped": 0}

    saved = skipped = 0

    for row in rows:
        result = await db["prices"].update_one(
            {"date": row["date"], "market": row["market"], "product": row["product"]},
            {"$setOnInsert": row},
            upsert=True,
        )
        if result.upserted_id:
            saved += 1
        else:
            skipped += 1

    return {"status": "ok", "saved": saved, "skipped": skipped, "total": len(rows)}


# -------------------------------------------------------
# ✅ Upload PDF (manual import from ICC)
# -------------------------------------------------------
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), db=Depends(get_db)):
    os.makedirs("uploads", exist_ok=True)
    path = f"uploads/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    rows = extract_prices_from_pdf(path)
    print("\n🔍 Parsed rows before DB insert:", rows)

    saved = 0
    for row in rows:
        result = await db["prices"].update_one(
            {"product": row["product"], "market": row["market"], "date": row["date"]},
            {"$setOnInsert": row},
            upsert=True,
        )
        if result.upserted_id:
            saved += 1

    return {"status": "success", "uploaded": file.filename, "saved_to_db": saved}


# -------------------------------------------------------
# ✅ NEW: Get list of products (dynamic from DB)
# -------------------------------------------------------
@app.get("/products")
async def get_products(db=Depends(get_db)):
    products = await db["prices"].distinct("product")
    return sorted(products)


# -------------------------------------------------------
# ✅ NEW: Get markets by selected product
# -------------------------------------------------------
@app.get("/markets-by-product")
async def get_markets_by_product(
    product: str = Query(...),
    db=Depends(get_db)
):
    markets = await db["prices"].distinct("market", {"product": product})
    return sorted(markets)


# -------------------------------------------------------
# ✅ NEW: Get prices filtered by product + market
# -------------------------------------------------------
@app.get("/prices-filtered")
async def get_filtered_prices(
    product: str = Query(...),
    market: str = Query(None),
    db=Depends(get_db)
):
    query = {"product": product}
    if market:
        query["market"] = market

    cursor = db["prices"].find(query, projection={"_id": 0}).sort("date", 1)
    return [doc async for doc in cursor]


# -------------------------------------------------------
# ✅ NEW: Analytics for dashboard (min, max, avg, and MoM%)
# -------------------------------------------------------
@app.get("/analytics")
async def get_analytics(
    product: str = Query(...),
    market: str = Query(...),
    db=Depends(get_db)
):
    cursor = db["prices"].find({"product": product, "market": market}).sort("date", 1)
    rows = [doc async for doc in cursor]

    if not rows:
        return {"message": "No data"}

    prices = [r["price"] for r in rows]
    mom_change_pct = None

    if len(prices) >= 2:
        mom_change_pct = ((prices[-1] - prices[-2]) / prices[-2]) * 100

    return {
        "product": product,
        "market": market,
        "min": min(prices),
        "max": max(prices),
        "avg": round(sum(prices) / len(prices), 2),
        "latest_price": prices[-1],
        "mom_change_percentage": round(mom_change_pct, 2) if mom_change_pct else None
    }


# -------------------------------------------------------
# ✅ OLD APIs (still supported)
# -------------------------------------------------------
@app.get("/markets")
async def list_markets(db=Depends(get_db)):
    return sorted(await db["prices"].distinct("market"))


@app.get("/prices")
async def get_prices(
    market: Optional[str] = Query(default=None),
    db=Depends(get_db)
):
    query = {}
    if market:
        query["market"] = market

    cursor = db["prices"].find(query, projection={"_id": 0}).sort("date", 1)
    return [doc async for doc in cursor]


@app.get("/stats")
async def get_stats(markets: Optional[List[str]] = Query(default=None), db=Depends(get_db)):
    cursor = db["prices"].find({})
    dataset = [doc async for doc in cursor]

    grouped = {}
    for rec in dataset:
        grouped.setdefault(rec["market"], []).append(rec)

    return {
        market: {
            "stats": basic_stats(rows),
            "monthly_avg": month_averages(rows),
            "mom": mom_change(month_averages(rows)),
        }
        for market, rows in grouped.items()
    }


@app.get("/compare")
async def compare(
    startA: datetime, endA: datetime,
    startB: datetime, endB: datetime,
    markets: Optional[List[str]] = Query(default=None),
    db=Depends(get_db)
):
    cursor = db["prices"].find({}).sort("date", 1)
    grouped = {}

    async for rec in cursor:
        grouped.setdefault(rec["market"], []).append(rec)

    return {
        market: compare_periods(rows, startA, endA, startB, endB)
        for market, rows in grouped.items()
    }

@app.delete("/clear-db")
async def clear_db(db=Depends(get_db)):
    result = await db["prices"].delete_many({})
    return {"deleted": result.deleted_count}
