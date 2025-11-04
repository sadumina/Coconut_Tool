import pdfplumber
import re
from datetime import datetime

def extract_prices_from_pdf(path: str):
    rows = []

    print("\n📄 Parsing PDF file:", path)

    with pdfplumber.open(path) as pdf:
        raw_text = "\n".join(page.extract_text() for page in pdf.pages)

    print("\n------ RAW TEXT (debug) ------")
    print(raw_text)
    print("------------------------------\n")

    # ✅ Extract date header row (week dates)
    date_matches = re.findall(r"(\d{2}/\d{2}/\d{4})", raw_text)
    print("📅 Extracted dates:", date_matches)
    column_dates = date_matches[:5]  # sometimes 4 or 5 weeks exist

    # ✅ Regex captures ANY PRODUCT + MARKET + PRICES
    pattern = r"([A-Za-z ()*,]+)\s+([A-Za-z ()/,]+)\s+([0-9\sNQ\.,-]+)"
    matches = re.findall(pattern, raw_text)

    print(f"🔍 Matched product rows: {len(matches)}")

    for product, market, price_block in matches:
        product = product.strip()
        market = market.strip()

        # Extract number fragments (can be broken like 6 18 → 618)
        digits = re.findall(r"(\d+)", price_block)

        print(f"\n➡️ {product} | {market}")
        print(f"   🧩 Raw number tokens: {digits}")

        # Fix broken numbers intelligently
        fixed_prices = []
        tmp = ""
        for d in digits:
            tmp += d
            if len(tmp) >= 3:  # coconut industry prices are 3+ digits
                fixed_prices.append(tmp)
                tmp = ""

        print(f"   ✅ Fixed prices: {fixed_prices}")

        # Insert into result set
        for i, price in enumerate(fixed_prices[:len(column_dates)]):
            rows.append({
                "product": product,
                "market": market,
                "price": float(price),
                "date": datetime.strptime(column_dates[i], "%d/%m/%Y"),
            })

    print(f"\n✅ FINAL ROW COUNT: {len(rows)} extracted")
    return rows
