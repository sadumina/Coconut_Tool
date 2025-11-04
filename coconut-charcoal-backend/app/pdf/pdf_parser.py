import pdfplumber
import re
from datetime import datetime

def extract_prices_from_pdf(path: str):
    rows = []

    print(f"\n📄 Parsing PDF: {path}")

    with pdfplumber.open(path) as pdf:
        lines = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.split("\n"))

    # DEBUG (optional)
    print("\n🟦 RAW LINES EXTRACTED FROM PDF (first 40 lines):")
    for idx, line in enumerate(lines[:40]):
        print(f"{idx}: {line}")

    # ✅ Extract dates from header line (week columns)
    date_matches = re.findall(r"(\d{2}/\d{2}/\d{4})", "\n".join(lines))
    print("\n📅 Week dates:", date_matches)

    if len(date_matches) == 0:
        print("❌ No week dates found. PDF format changed.")
        return []

    week_dates = date_matches[:5]  # Max 5 weeks

    # ✅ Process table rows
    current_product = None
    current_market = None

    for line in lines:
        line = line.strip()

        # skip headers and footers
        if ("Note:" in line) or ("Source:" in line) or line.startswith("Products"):
            continue

        # Detect product + market
        # Example match: "Coconut Shell Charcoal Indonesia (FOB)"
        product_market_match = re.match(r"([A-Za-z ]+?)\s+([A-Za-z]+.*)", line)

        if product_market_match and not re.search(r"\d", line):
            current_product = product_market_match.group(1).strip()
            current_market = product_market_match.group(2).strip()
            continue

        # ✅ Detect a price row (must contain numbers)
        price_tokens = re.findall(r"\d[\d\s,]*", line)

        if current_product and price_tokens:
            cleaned_prices = []

            # Fix fragmented numbers like "3 206" -> "3206"
            tmp = ""
            for token in price_tokens:
                token = token.replace(",", "").strip()
                tmp += token
                if len(tmp) >= 3:
                    cleaned_prices.append(tmp)
                    tmp = ""

            # Insert rows only when price count equals week dates count
            if len(cleaned_prices) == len(week_dates):
                print(f"➡️ {current_product} | {current_market} → {cleaned_prices}")

                for i, price in enumerate(cleaned_prices):
                    rows.append({
                        "product": current_product,
                        "market": current_market,
                        "price": float(price),
                        "date": datetime.strptime(week_dates[i], "%d/%m/%Y"),
                    })

    print(f"\n✅ FINAL PDF ROW COUNT: {len(rows)} records returned.")
    return rows
