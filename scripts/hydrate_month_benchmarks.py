import json
import os
import re
import sys
from urllib.parse import urlencode
from urllib.request import urlopen


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONTHS_DIR = os.path.join(DATA_DIR, "months")

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


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


def try_fetch_dnb_nav():
    # Første forsøk: Euronext Live-side for DNB Global Indeks A.
    # Denne delen er bevisst defensiv fordi kilden ikke er en enkel dokumentert NAV-API.
    url = "https://live.euronext.com/nb/product/funds/NO0010582984.DKGLBIX-WOMF"

    try:
        with urlopen(url) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception as exc:
        raise ValueError(f"Kunne ikke hente DNB-kilde: {exc}")

    # Forsøk å finne en pris i innebygget HTML/JS. Dette kan kreve justering senere.
    patterns = [
        r'"lastPrice"\s*:\s*"?(?P<price>\d+[.,]\d+)"?',
        r'"price"\s*:\s*"?(?P<price>\d+[.,]\d+)"?',
        r'"close"\s*:\s*"?(?P<price>\d+[.,]\d+)"?',
        r'data-last-price\s*=\s*"(?P<price>\d+[.,]\d+)"'
    ]

    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            value = match.group("price").replace(",", ".")
            return float(value)

    raise ValueError("Fant ikke DNB NAV/price i kilden")


def main():
    if len(sys.argv) != 2:
        print("Bruk: python3 scripts/hydrate_month_benchmarks.py 2026-05")
        sys.exit(1)

    month_id = sys.argv[1]
    month_path = os.path.join(MONTHS_DIR, f"{month_id}.json")
    month = load_json(month_path)

    spy_price = fetch_finnhub_quote(month["benchmarks"]["sp500_proxy_ticker"])
    month["benchmarks"]["sp500_buy_price"] = round(spy_price, 4)

    try:
        dnb_nav = try_fetch_dnb_nav()
        month["benchmarks"]["dnb_global_indeks_buy_nav"] = round(dnb_nav, 4)
    except Exception as exc:
        print(f"Advarsel: klarte ikke å hente DNB Global Indeks automatisk: {exc}")

    save_json(month_path, month)
    print(f"Oppdaterte benchmark-startverdier i {month_path}")


if __name__ == "__main__":
    main()