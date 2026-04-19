import json
import os
import re
import sys
from urllib.parse import urlencode
from urllib.request import urlopen, Request


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONTHS_DIR = os.path.join(DATA_DIR, "months")

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

DNB_FUND_URL = "https://www.dnb.no/sparing/fond/fond-liste/d/dnb-global-indeks-a-NO0010582984"
EURONEXT_FUND_URL = "https://live.euronext.com/nb/product/funds/NO0010582984.DKGLBIX-WOMF"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fetch_text(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "nb-NO,nb;q=0.9,en;q=0.8"
        },
    )
    with urlopen(request) as response:
        return response.read().decode("utf-8", errors="ignore")


def fetch_finnhub_quote(symbol):
    if not FINNHUB_API_KEY:
        raise ValueError("FINNHUB_API_KEY mangler")

    params = urlencode({"symbol": symbol, "token": FINNHUB_API_KEY})
    url = f"https://finnhub.io/api/v1/quote?{params}"
    with urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))

    price = data.get("c")
    if price in (None, 0):
        raise ValueError(f"Ingen gyldig Finnhub-pris for {symbol}: {data}")

    return float(price)


def normalize_number(value):
    value = value.replace("\xa0", " ").replace(" ", "")
    value = value.replace(",", ".")
    return float(value)


def try_fetch_dnb_nav_from_dnb():
    html = fetch_text(DNB_FUND_URL)

    # Gjør teksten enklere å søke i
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    # Se etter NAV/Kurs ... 794,22 kroner ... 15. apr. 2026
    pattern = r"NAV/Kurs\s+(?P<nav>\d+[.,]\d+)\s+kroner\s+(?P<date>\d{1,2}\.\s*[A-Za-zæøåÆØÅ]{3,}\.?\s*\d{4})"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        nav = normalize_number(match.group("nav"))
        date = match.group("date").strip()
        return {"nav": nav, "date": date, "source": "dnb.no"}

    # Reserveforsøk: finn NAV/Kurs og søk i et lite tekstvindu etterpå
    anchor = re.search(r"NAV/Kurs", text, re.IGNORECASE)
    if anchor:
        snippet = text[anchor.start(): anchor.start() + 300]

        nav_match = re.search(r"(\d+[.,]\d+)\s+kroner", snippet, re.IGNORECASE)
        date_match = re.search(r"(\d{1,2}\.\s*[A-Za-zæøåÆØÅ]{3,}\.?\s*\d{4})", snippet, re.IGNORECASE)

        if nav_match and date_match:
            nav = normalize_number(nav_match.group(1))
            date = date_match.group(1).strip()
            return {"nav": nav, "date": date, "source": "dnb.no"}

    raise ValueError("Fant ikke NAV/Kurs på DNB-siden")


def try_fetch_dnb_nav_from_euronext():
    html = fetch_text(EURONEXT_FUND_URL)

    patterns = [
        r'"lastPrice"\s*:\s*"?(?P<nav>\d+[.,]\d+)"?',
        r'"price"\s*:\s*"?(?P<nav>\d+[.,]\d+)"?',
        r'"close"\s*:\s*"?(?P<nav>\d+[.,]\d+)"?',
        r'data-last-price\s*=\s*"(?P<nav>\d+[.,]\d+)"'
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            nav = normalize_number(match.group("nav"))
            return {"nav": nav, "date": None, "source": "euronext"}

    raise ValueError("Fant ikke pris/NAV på Euronext-siden")


def try_fetch_dnb_nav():
    errors = []

    try:
        return try_fetch_dnb_nav_from_dnb()
    except Exception as exc:
        errors.append(f"DNB-kilde feilet: {exc}")

    try:
        return try_fetch_dnb_nav_from_euronext()
    except Exception as exc:
        errors.append(f"Euronext-kilde feilet: {exc}")

    raise ValueError(" | ".join(errors))


def main():
    if len(sys.argv) != 2:
        print("Bruk: python3 scripts/hydrate_month_benchmarks.py 2026-05")
        sys.exit(1)

    month_id = sys.argv[1]
    month_path = os.path.join(MONTHS_DIR, f"{month_id}.json")
    month = load_json(month_path)

    spy_price = fetch_finnhub_quote(month["benchmarks"]["sp500_proxy_ticker"])
    month["benchmarks"]["sp500_buy_price"] = round(spy_price, 4)
    print(f"SPY/benchmark satt til {month['benchmarks']['sp500_buy_price']}")

    try:
        dnb_data = try_fetch_dnb_nav()
        month["benchmarks"]["dnb_global_indeks_buy_nav"] = round(dnb_data["nav"], 4)
        if dnb_data["date"]:
            month["benchmarks"]["dnb_global_indeks_as_of_date"] = dnb_data["date"]
        print(
            f"DNB Global Indeks satt til {month['benchmarks']['dnb_global_indeks_buy_nav']}"
            f" (kilde: {dnb_data['source']})"
        )
    except Exception as exc:
        print(f"Advarsel: klarte ikke å hente DNB Global Indeks automatisk: {exc}")

    save_json(month_path, month)
    print(f"Oppdaterte benchmark-startverdier i {month_path}")


if __name__ == "__main__":
    main()