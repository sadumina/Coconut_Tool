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
from .scraper.icc_scraper import scrape_icc    # <-- Sync scraper
from .pdf.pdf_parser import extract_prices_from_pdf


app = FastAPI(
    title="Coconut Shell Charcoal API",
    version="1.0.0"
)

# -------------------------------------------------------
# ✅ CORS for frontend
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
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
    print("🔄 Starting scrape job...")

    # ⬅ Run Playwright (sync) inside threadpool (because FastAPI is async)
    rows = await run_in_threadpool(scrape_icc)

    if not rows:
        print("⚠️ No data extracted / Cloudflare blocked")
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
# ✅ Upload PDF (manual data import)
# -------------------------------------------------------
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), db=Depends(get_db)):
    path = f"uploads/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    from .pdf.pdf_parser import extract_prices_from_pdf

    rows = extract_prices_from_pdf(path)

    print("\n🔍 Parsed rows before DB insert:")
    for r in rows:
        print(r)

    saved = 0
    for row in rows:
        result = await db["prices"].update_one(
            {"market": row["market"], "product": row["product"], "date": row["date"]},
            {"$setOnInsert": row},
            upsert=True,
        )
        if result.upserted_id:
            saved += 1

    return {"status": "success", "uploaded": file.filename, "saved_to_db": saved}



# -------------------------------------------------------
# ✅ List markets
# -------------------------------------------------------
@app.get("/markets")
async def list_markets(db=Depends(get_db)):
    return sorted(await db["prices"].distinct("market"))


# -------------------------------------------------------
# ✅ Get raw price dataset
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
# ✅ Aggregated statistics for charts
# -------------------------------------------------------
@app.get("/stats")
async def get_stats(markets: Optional[List[str]] = Query(default=None), db=Depends(get_db)):
    query = {"product": "Coconut Shell Charcoal"}
    if markets:
        query["market"] = {"$in": markets}

    cursor = db["prices"].find(query)
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


# -------------------------------------------------------
# ✅ Compare two periods (dashboard feature)
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

    return {
        market: compare_periods(rows, startA, endA, startB, endB)
        for market, rows in grouped.items()
    }
