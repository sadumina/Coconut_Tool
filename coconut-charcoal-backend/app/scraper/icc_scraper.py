"""
ICC Price Scraper (ScraperAPI version)
--------------------------------------
✅ Bypasses Cloudflare
✅ No Selenium / Chrome needed
✅ Uses BeautifulSoup to parse tables
"""

from datetime import datetime
import os
import re
from typing import List, Dict
from bs4 import BeautifulSoup
import requests

URL = "https://coconutcommunity.org/page-statistics/weekly-price-update"
TARGET_PRODUCT = "coconut shell charcoal".lower()

SCRAPER_API_KEY = "1b6f8abd3ac9b68568788ca207358da1"  # ✅ your key here


def _dump_html_for_debug(html: str, name: str = "icc_page_debug.html"):
    """Save HTML locally so we can inspect when debugging"""
    out = os.path.join(os.getcwd(), name)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"🔍 Saved page HTML to: {out}")


def scrape_icc() -> List[Dict]:
    print("🟡 Fetching page via ScraperAPI (Cloudflare bypass)…")

    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&render=true&url={URL}"

    try:
        resp = requests.get(api_url, timeout=30)
    except Exception as e:
        print("❌ Network error:", e)
        return []

    if resp.status_code != 200:
        print(f"❌ ScraperAPI failed. HTTP {resp.status_code}")
        return []

    html = resp.text
    _dump_html_for_debug(html)  # ✅ save returned HTML

    # detect Cloudflare / blocked
    lower = html.lower()
    if "cloudflare" in lower or "captcha" in lower or "verify you are human" in lower:
        print("⚠️ Cloudflare still blocking — returning empty")
        return []

    soup = BeautifulSoup(html, "lxml")

    rows = []

    # find all <table> elements
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

        if not headers:
            continue

        if "product" not in " ".join(headers):
            continue

        # find indices
        def idx_contains(words):
            for i, h in enumerate(headers):
                if any(w in h for w in words):
                    return i
            return None

        product_idx = idx_contains(["product"])
        market_idx = idx_contains(["market", "country"])
        price_idx = idx_contains(["price", "usd", "$", "value"])

        if product_idx is None or price_idx is None:
            continue

        # iterate table rows
        for tr in table.find_all("tr")[1:]:
            tds = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(tds) < max(product_idx, price_idx) + 1:
                continue

            product_text = tds[product_idx].lower()
            if TARGET_PRODUCT not in product_text:
                continue

            market = tds[market_idx] if market_idx is not None else "Unknown"

            price_raw = tds[price_idx].replace(",", "").replace("USD", "").strip()
            price_clean = re.sub(r"[^\d.]+", "", price_raw)

            try:
                price_value = float(price_clean)
            except:
                continue

            rows.append({
                "date": datetime.utcnow(),
                "market": market,
                "product": "Coconut Shell Charcoal",
                "price": price_value,
                "currency": "USD",
                "unit": "per tonne",
                "source_url": URL
            })

    print(f"✅ Extracted {len(rows)} rows from ICC table")
    return rows
