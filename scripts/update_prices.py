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
PERFORMANCE_PATH = os.path.join(DATA_DIR, "performance.json")

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


def calculate_portfolio_return(positions):
    if not positions:
        return 0.0
    total = sum(position["return_pct"] for position in positions)
    return total / len(positions)


def find_best_contributor(positions):
    return max(positions, key=lambda p: p["return_pct"])


def find_worst_contributor(positions):
    return min(positions, key=lambda p: p["return_pct"])


def main():
    if not API_KEY:
        print("FINNHUB_API_KEY mangler.")
        sys.exit(1)

    portfolio = load_json(CURRENT_PORTFOLIO_PATH)
    benchmarks = load_json(BENCHMARKS_PATH)
    performance = load_json(PERFORMANCE_PATH)

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

    portfolio_return = round(calculate_portfolio_return(portfolio["positions"]), 4)
    alpha_vs_sp500 = round(portfolio_return - benchmarks["sp500"]["return_pct"], 4)
    alpha_vs_dnb = round(
        portfolio_return - benchmarks["dnb_global_indeks"]["return_pct"],
        4
    )

    best = find_best_contributor(portfolio["positions"])
    worst = find_worst_contributor(portfolio["positions"])

    performance["month_id"] = portfolio["month_id"]
    performance["updated_at"] = updated_at
    performance["portfolio_return_pct"] = portfolio_return
    performance["alpha_vs_sp500"] = alpha_vs_sp500
    performance["alpha_vs_dnb"] = alpha_vs_dnb
    performance["best_contributor"] = {
        "ticker": best["ticker"],
        "return_pct": round(best["return_pct"], 4)
    }
    performance["worst_contributor"] = {
        "ticker": worst["ticker"],
        "return_pct": round(worst["return_pct"], 4)
    }

    portfolio["updated_at"] = updated_at
    benchmarks["updated_at"] = updated_at

    save_json(CURRENT_PORTFOLIO_PATH, portfolio)
    save_json(BENCHMARKS_PATH, benchmarks)
    save_json(PERFORMANCE_PATH, performance)

    print("Oppdaterte priser, benchmarks og performance.")
    print(f"updated_at={updated_at}")


if __name__ == "__main__":
    main()