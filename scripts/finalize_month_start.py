import json
import os
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


def main():
    if len(sys.argv) != 2:
        print("Bruk: python3 scripts/finalize_month_start.py 2026-05")
        sys.exit(1)

    month_id = sys.argv[1]
    month_path = os.path.join(MONTHS_DIR, f"{month_id}.json")
    month = load_json(month_path)

    if not FINNHUB_API_KEY:
        print("FINNHUB_API_KEY mangler.")
        sys.exit(1)

    print(f"Finaliserer månedstart for {month_id} ...")

    for position in month["positions"]:
        ticker = position["ticker"]
        price = fetch_finnhub_quote(ticker)
        position["buy_price"] = round(price, 4)
        print(f"- {ticker}: buy_price satt til {position['buy_price']}")

    spy_ticker = month["benchmarks"]["sp500_proxy_ticker"]
    spy_price = fetch_finnhub_quote(spy_ticker)
    month["benchmarks"]["sp500_buy_price"] = round(spy_price, 4)
    print(f"- {spy_ticker}: sp500_buy_price satt til {month['benchmarks']['sp500_buy_price']}")

    # DNB beholdes som den er hvis hydrate-scriptet ikke fant noe.
    if month["benchmarks"]["dnb_global_indeks_buy_nav"] is None:
        print("- DNB Global Indeks buy NAV er fortsatt null (ok foreløpig)")

    save_json(month_path, month)
    print(f"Oppdaterte kjøpskurser i {month_path}")


if __name__ == "__main__":
    main()