import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

NEW_MONTH_INPUT_PATH = os.path.join(DATA_DIR, "new_month_input.json")
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


def build_current_portfolio(source):
    return {
        "month_id": source["month_id"],
        "label": source["label"],
        "buy_date": source["buy_date"],
        "status": "active",
        "positions": [
            {
                "ticker": position["ticker"],
                "company": position["company"],
                "exchange": position["exchange"],
                "country": position["country"],
                "sector": position["sector"],
                "buy_price": position["buy_price"],
                "current_price": position["buy_price"],
                "return_pct": 0,
                "weight": position["weight"],
                "thesis": position["thesis"],
                "catalysts_30d": position["catalysts_30d"],
                "risk": position["risk"]
            }
            for position in source["positions"]
        ]
    }


def build_benchmarks(source):
    return {
        "month_id": source["month_id"],
        "buy_date": source["buy_date"],
        "sp500": {
            "name": source["sp500"]["name"],
            "proxy_ticker": source["sp500"]["proxy_ticker"],
            "buy_price": source["sp500"]["buy_price"],
            "current_price": source["sp500"]["buy_price"],
            "return_pct": 0
        },
        "dnb_global_indeks": {
            "name": source["dnb_global_indeks"]["name"],
            "buy_nav": source["dnb_global_indeks"]["buy_nav"],
            "current_nav": source["dnb_global_indeks"]["current_nav"],
            "return_pct": source["dnb_global_indeks"]["return_pct"],
            "as_of_date": source["dnb_global_indeks"]["as_of_date"]
        }
    }


def build_updates(source):
    return {
        "month_id": source["month_id"],
        "initial_pick_note": source["initial_pick_note"],
        "midmonth_update": None
    }


def build_performance(source):
    return {
        "month_id": source["month_id"],
        "updated_at": None,
        "portfolio_return_pct": 0,
        "alpha_vs_sp500": 0,
        "alpha_vs_dnb": 0,
        "best_contributor": {
            "ticker": "",
            "return_pct": 0
        },
        "worst_contributor": {
            "ticker": "",
            "return_pct": 0
        }
    }


def main():
    source = load_json(NEW_MONTH_INPUT_PATH)

    current_portfolio = build_current_portfolio(source)
    benchmarks = build_benchmarks(source)
    updates = build_updates(source)
    performance = build_performance(source)

    save_json(CURRENT_PORTFOLIO_PATH, current_portfolio)
    save_json(BENCHMARKS_PATH, benchmarks)
    save_json(UPDATES_PATH, updates)
    save_json(PERFORMANCE_PATH, performance)

    print(f"Ny måned klargjort: {source['label']}")


if __name__ == "__main__":
    main()