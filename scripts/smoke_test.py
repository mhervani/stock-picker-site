import json
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONTHS_DIR = os.path.join(DATA_DIR, "months")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def assert_file_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Mangler fil: {path}")


def assert_keys(obj, keys, label):
    missing = [key for key in keys if key not in obj]
    if missing:
        raise KeyError(f"{label} mangler nøkler: {', '.join(missing)}")


def main():
    files_to_check = [
        os.path.join(DATA_DIR, "current_portfolio.json"),
        os.path.join(DATA_DIR, "benchmarks.json"),
        os.path.join(DATA_DIR, "updates.json"),
        os.path.join(DATA_DIR, "performance.json"),
        os.path.join(DATA_DIR, "chart_data.json"),
        os.path.join(DATA_DIR, "held_positions.json"),
        os.path.join(DATA_DIR, "monthly_history.json"),
        os.path.join(DATA_DIR, "track_record.json"),
        os.path.join(MONTHS_DIR, "index.json"),
    ]

    for path in files_to_check:
        assert_file_exists(path)

    current_portfolio = load_json(os.path.join(DATA_DIR, "current_portfolio.json"))
    benchmarks = load_json(os.path.join(DATA_DIR, "benchmarks.json"))
    performance = load_json(os.path.join(DATA_DIR, "performance.json"))
    chart_data = load_json(os.path.join(DATA_DIR, "chart_data.json"))
    held_positions = load_json(os.path.join(DATA_DIR, "held_positions.json"))
    months_index = load_json(os.path.join(MONTHS_DIR, "index.json"))

    assert_keys(current_portfolio, ["month_id", "label", "buy_date", "positions"], "current_portfolio.json")
    assert_keys(benchmarks, ["month_id", "buy_date", "sp500", "dnb_global_indeks"], "benchmarks.json")
    assert_keys(performance, ["month_id", "portfolio_return_pct", "alpha_vs_sp500", "alpha_vs_dnb"], "performance.json")
    assert_keys(chart_data, ["month_id", "series"], "chart_data.json")
    assert_keys(held_positions, ["portfolios"], "held_positions.json")
    assert_keys(months_index, ["active_month", "months"], "data/months/index.json")

    if not isinstance(current_portfolio["positions"], list) or len(current_portfolio["positions"]) != 3:
        raise ValueError("current_portfolio.json må ha nøyaktig 3 posisjoner")

    active_month = months_index["active_month"]
    if active_month:
        month_path = os.path.join(MONTHS_DIR, f"{active_month}.json")
        assert_file_exists(month_path)
        month_file = load_json(month_path)
        assert_keys(month_file, ["month_id", "label", "status", "buy_date", "market_context", "portfolio", "positions"], f"{active_month}.json")

    print("Smoke test OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Smoke test feilet: {exc}")
        sys.exit(1)