import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import urlopen
from urllib.parse import urlencode

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CURRENT_PORTFOLIO_PATH = os.path.join(DATA_DIR, "current_portfolio.json")
BENCHMARKS_PATH = os.path.join(DATA_DIR, "benchmarks.json")

API_KEY = os.getenv("FINNHUB_API_KEY")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fetch_quote(symbol):
    params = urlencode({
        "symbol": symbol,
        "token": API_KEY,
    })
    url = f"https://finnhub.io/api/v1/quote?{params}"

    with urlopen(url) as response:
        raw = response.read().decode("utf-8")
        data = json.loads(raw)

    current_price = data.get("c")
    previous_close = data.get("pc")

    if current_price in (None, 0):
        raise ValueError(f"Ingen gyldig pris for {symbol}: {data}")

    return {
        "current_price": float(current_price),
        "previous_close": float(previous_close) if previous_close else None
    }


def calculate_return_pct(buy_price, current_price):
    return ((current_price - buy_price) / buy_price) * 100


def main():
    if not API_KEY:
        print("FINNHUB_API_KEY mangler.")
        sys.exit(1)

    portfolio = load_json(CURRENT_PORTFOLIO_PATH)
    benchmarks = load_json(BENCHMARKS_PATH)

    updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    for position in portfolio["positions"]:
        symbol = position["ticker"]
        quote = fetch_quote(symbol)
        position["current_price"] = round(quote["current_price"], 4)
        position["return_pct"] = round(
            calculate_return_pct(position["buy_price"], position["current_price"]),
            4
        )

    sp500_symbol = benchmarks["sp500"]["proxy_ticker"]
    sp500_quote = fetch_quote(sp500_symbol)
    benchmarks["sp500"]["current_price"] = round(sp500_quote["current_price"], 4)
    benchmarks["sp500"]["return_pct"] = round(
        calculate_return_pct(
            benchmarks["sp500"]["buy_price"],
            benchmarks["sp500"]["current_price"]
        ),
        4
    )

    portfolio["updated_at"] = updated_at
    benchmarks["updated_at"] = updated_at

    save_json(CURRENT_PORTFOLIO_PATH, portfolio)
    save_json(BENCHMARKS_PATH, benchmarks)

    print("Oppdaterte priser for portefølje og S&P 500-proxy.")
    print(f"updated_at={updated_at}")


if __name__ == "__main__":
    main()