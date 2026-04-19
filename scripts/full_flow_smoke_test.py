import json
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONTHS_DIR = os.path.join(DATA_DIR, "months")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def assert_true(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    current_portfolio = load_json(os.path.join(DATA_DIR, "current_portfolio.json"))
    benchmarks = load_json(os.path.join(DATA_DIR, "benchmarks.json"))
    performance = load_json(os.path.join(DATA_DIR, "performance.json"))
    chart_data = load_json(os.path.join(DATA_DIR, "chart_data.json"))
    held_positions = load_json(os.path.join(DATA_DIR, "held_positions.json"))
    months_index = load_json(os.path.join(MONTHS_DIR, "index.json"))

    assert_true(current_portfolio["month_id"] == months_index["active_month"], "Aktiv måned matcher ikke index.json")
    assert_true(len(current_portfolio["positions"]) == 3, "Aktiv portefølje må ha 3 posisjoner")
    assert_true(benchmarks["sp500"]["buy_price"] not in (None, 0), "SP500 buy_price mangler")
    assert_true(benchmarks["dnb_global_indeks"]["buy_nav"] not in (None, 0), "DNB buy_nav mangler")
    assert_true(chart_data["month_id"] == current_portfolio["month_id"], "chart_data month_id matcher ikke aktiv måned")
    assert_true(isinstance(chart_data["series"], list), "chart_data.series må være en liste")
    assert_true("portfolios" in held_positions, "held_positions.json mangler portfolios")

    active_month_path = os.path.join(MONTHS_DIR, f"{months_index['active_month']}.json")
    active_month = load_json(active_month_path)

    assert_true(active_month["month_id"] == current_portfolio["month_id"], "Aktiv månedsfil matcher ikke current_portfolio")
    assert_true(isinstance(active_month["positions"], list) and len(active_month["positions"]) == 3, "Aktiv månedsfil må ha 3 picks")

    print("Full flow smoke test OK")
    print(f"Aktiv måned: {current_portfolio['month_id']}")
    print(f"Chart-punkter: {len(chart_data['series'])}")
    print(f"What-if-held porteføljer: {len(held_positions['portfolios'])}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Full flow smoke test feilet: {exc}")
        sys.exit(1)