import json
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONTHS_DIR = os.path.join(DATA_DIR, "months")

CURRENT_PORTFOLIO_PATH = os.path.join(DATA_DIR, "current_portfolio.json")
BENCHMARKS_PATH = os.path.join(DATA_DIR, "benchmarks.json")
UPDATES_PATH = os.path.join(DATA_DIR, "updates.json")
PERFORMANCE_PATH = os.path.join(DATA_DIR, "performance.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    if len(sys.argv) != 2:
        print("Bruk: python3 scripts/apply_month_to_active.py 2026-05")
        sys.exit(1)

    month_id = sys.argv[1]
    month_path = os.path.join(MONTHS_DIR, f"{month_id}.json")
    month = load_json(month_path)

    current_portfolio = {
        "month_id": month["month_id"],
        "label": month["label"],
        "buy_date": month["buy_date"],
        "status": month["status"],
        "updated_at": None,
        "positions": [
            {
                "ticker": p["ticker"],
                "company": p["company"],
                "exchange": p["exchange"],
                "country": p["country"],
                "sector": p["sector"],
                "buy_price": p["buy_price"],
                "current_price": p["buy_price"],
                "return_pct": 0,
                "weight": p["weight"],
                "thesis": p["thesis"],
                "catalysts_30d": p["catalysts"],
                "risk": p["risk"]
            }
            for p in month["positions"]
        ]
    }

    benchmarks = {
        "month_id": month["month_id"],
        "buy_date": month["buy_date"],
        "updated_at": None,
        "sp500": {
            "name": month["benchmarks"]["primary"],
            "proxy_ticker": month["benchmarks"]["sp500_proxy_ticker"],
            "buy_price": month["benchmarks"]["sp500_buy_price"],
            "current_price": month["benchmarks"]["sp500_buy_price"],
            "return_pct": 0
        },
        "dnb_global_indeks": {
            "name": month["benchmarks"]["secondary"],
            "buy_nav": month["benchmarks"]["dnb_global_indeks_buy_nav"],
            "current_nav": month["benchmarks"]["dnb_global_indeks_buy_nav"],
            "return_pct": None if month["benchmarks"]["dnb_global_indeks_buy_nav"] in (None, 0) else 0,
            "as_of_date": month["benchmarks"]["dnb_global_indeks_as_of_date"]
        }
    }

    updates = {
        "month_id": month["month_id"],
        "initial_pick_note": month["portfolio"]["why_this_portfolio_can_win"],
        "midmonth_update": month["midmonth_update"]
    }

    performance = {
        "month_id": month["month_id"],
        "updated_at": None,
        "portfolio_return_pct": 0,
        "alpha_vs_sp500": 0,
        "alpha_vs_dnb": None if month["benchmarks"]["dnb_global_indeks_buy_nav"] in (None, 0) else 0,
        "best_contributor": {
            "ticker": "",
            "return_pct": 0
        },
        "worst_contributor": {
            "ticker": "",
            "return_pct": 0
        }
    }

    save_json(CURRENT_PORTFOLIO_PATH, current_portfolio)
    save_json(BENCHMARKS_PATH, benchmarks)
    save_json(UPDATES_PATH, updates)
    save_json(PERFORMANCE_PATH, performance)

    print(f"Aktiv måned satt til {month_id}")


if __name__ == "__main__":
    main()