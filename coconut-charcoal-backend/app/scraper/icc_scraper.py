# app/scraper/icc_scraper.py

from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import random, time, re


URL = "https://coconutcommunity.org/page-statistics/weekly-price-update"
TARGET_PRODUCT = "coconut shell charcoal"


def simulate_human(page):
    page.mouse.move(random.randint(50, 800), random.randint(50, 500))
    page.mouse.wheel(0, random.randint(200, 1600))
    time.sleep(random.uniform(1.5, 3))


def scrape_icc():
    print("🟡 Launching Playwright browser (stealth)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # ✅ must run visible until Cloudflare cleared
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            viewport={"width": 1550, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.6099.224 Safari/537.36"
            )
        )

        # remove webdriver flag
        context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")

        page = context.new_page()
        page.set_default_timeout(120000)

        print("🌍 Navigating...")
        page.goto(URL, wait_until="domcontentloaded")  # ⬅ IMPORTANT

        # ✅ Cloudflare bypass loop
        for i in range(15):  # max ~25 sec
            if "Verifying you are human" not in page.content():
                break

            print(f"⏳ Cloudflare challenge... ({i+1}/15)")
            simulate_human(page)
            time.sleep(2)

        # scroll & act human
        simulate_human(page)

        # ✅ Wait until table is present (retry based wait)
        for i in range(20):
            try:
                page.locator("table").first.wait_for(timeout=2000)
                print("✅ Table loaded!")
                break
            except PlaywrightTimeout:
                print("⏳ Waiting table...", i + 1)
                simulate_human(page)

        html = page.content()

        # save HTML to debug
        with open("icc_debug.html", "w", encoding="utf-8") as f:
            f.write(html)

        soup = BeautifulSoup(html, "lxml")

        rows = []
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if not headers or "product" not in " ".join(headers):
                continue

            p_idx = next((i for i, h in enumerate(headers) if "product" in h), None)
            price_idx = next((i for i, h in enumerate(headers) if "usd" in h or "$" in h), None)
            market_idx = next((i for i, h in enumerate(headers) if "market" in h or "country" in h), None)

            for tr in table.find_all("tr")[1:]:
                tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                if len(tds) <= max(p_idx, price_idx):
                    continue

                if TARGET_PRODUCT not in tds[p_idx].lower():
                    continue

                price_clean = re.sub(r"[^\d.]", "", tds[price_idx])
                if price_clean:
                    rows.append({
                        "date": datetime.utcnow(),
                        "market": tds[market_idx] if market_idx else "Unknown",
                        "product": "Coconut Shell Charcoal",
                        "price": float(price_clean),
                        "currency": "USD",
                        "unit": "per tonne",
                        "source_url": URL,
                    })

        browser.close()
        print(f"✅ Extracted {len(rows)} rows")
        return rows
