import json
import os
import sys
from typing import Any, Dict, List, Tuple


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONTHS_DIR = os.path.join(DATA_DIR, "months")
RAW_DIR = os.path.join(DATA_DIR, "raw")

CURRENT_PORTFOLIO_PATH = os.path.join(DATA_DIR, "current_portfolio.json")
BENCHMARKS_PATH = os.path.join(DATA_DIR, "benchmarks.json")
UPDATES_PATH = os.path.join(DATA_DIR, "updates.json")
PERFORMANCE_PATH = os.path.join(DATA_DIR, "performance.json")
CHART_DATA_PATH = os.path.join(DATA_DIR, "chart_data.json")
HELD_POSITIONS_PATH = os.path.join(DATA_DIR, "held_positions.json")
MONTHLY_HISTORY_PATH = os.path.join(DATA_DIR, "monthly_history.json")
TRACK_RECORD_PATH = os.path.join(DATA_DIR, "track_record.json")
MONTHS_INDEX_PATH = os.path.join(MONTHS_DIR, "index.json")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def exists(path: str) -> bool:
    return os.path.exists(path)


def fmt(value: Any) -> str:
    if value is None:
        return "null"
    return str(value)


def add_result(results: List[Tuple[str, str, str]], level: str, label: str, detail: str) -> None:
    results.append((level, label, detail))


def check_file_exists(results: List[Tuple[str, str, str]], path: str, label: str) -> bool:
    if exists(path):
        add_result(results, "OK", label, path)
        return True
    add_result(results, "ERROR", label, f"Mangler fil: {path}")
    return False


def get_active_month_file_path(active_month_id: str) -> str:
    return os.path.join(MONTHS_DIR, f"{active_month_id}.json")


def main() -> None:
    results: List[Tuple[str, str, str]] = []

    # 1. Sjekk at nøkkelfiler finnes
    required_files = [
        (CURRENT_PORTFOLIO_PATH, "current_portfolio.json"),
        (BENCHMARKS_PATH, "benchmarks.json"),
        (UPDATES_PATH, "updates.json"),
        (PERFORMANCE_PATH, "performance.json"),
        (CHART_DATA_PATH, "chart_data.json"),
        (HELD_POSITIONS_PATH, "held_positions.json"),
        (MONTHLY_HISTORY_PATH, "monthly_history.json"),
        (TRACK_RECORD_PATH, "track_record.json"),
        (MONTHS_INDEX_PATH, "data/months/index.json"),
    ]

    all_required_exist = True
    for path, label in required_files:
        if not check_file_exists(results, path, label):
            all_required_exist = False

    if not all_required_exist:
        print_report(results)
        sys.exit(1)

    # 2. Last filer
    current_portfolio = load_json(CURRENT_PORTFOLIO_PATH)
    benchmarks = load_json(BENCHMARKS_PATH)
    updates = load_json(UPDATES_PATH)
    performance = load_json(PERFORMANCE_PATH)
    chart_data = load_json(CHART_DATA_PATH)
    held_positions = load_json(HELD_POSITIONS_PATH)
    monthly_history = load_json(MONTHLY_HISTORY_PATH)
    track_record = load_json(TRACK_RECORD_PATH)
    months_index = load_json(MONTHS_INDEX_PATH)

    active_month_id = months_index.get("active_month")
    if not active_month_id:
        add_result(results, "ERROR", "active_month", "index.json mangler active_month")
        print_report(results)
        sys.exit(1)

    add_result(results, "OK", "active_month", active_month_id)

    active_month_path = get_active_month_file_path(active_month_id)
    if not check_file_exists(results, active_month_path, "aktiv månedsfil"):
        print_report(results)
        sys.exit(1)

    active_month = load_json(active_month_path)

    # 3. Sjekk grunnleggende aktive metadata
    compare_scalar(results, "month_id current_portfolio", current_portfolio.get("month_id"), active_month_id)
    compare_scalar(results, "month_id benchmarks", benchmarks.get("month_id"), active_month_id)
    compare_scalar(results, "month_id updates", updates.get("month_id"), active_month_id)
    compare_scalar(results, "month_id performance", performance.get("month_id"), active_month_id)
    compare_scalar(results, "month_id chart_data", chart_data.get("month_id"), active_month_id)

    compare_scalar(results, "label", current_portfolio.get("label"), active_month.get("label"))
    compare_scalar(results, "buy_date current vs month", current_portfolio.get("buy_date"), active_month.get("buy_date"))
    compare_scalar(results, "buy_date benchmarks vs month", benchmarks.get("buy_date"), active_month.get("buy_date"))

    # 4. Sjekk brukerens viktigste felter
    month_id = active_month.get("month_id")
    label = active_month.get("label")
    buy_date = active_month.get("buy_date")
    analysis_date = active_month.get("analysis_date")

    if month_id and label and buy_date:
        add_result(
            results,
            "INFO",
            "aktiv måned oppsummert",
            f"month_id={month_id}, label={label}, buy_date={buy_date}, analysis_date={fmt(analysis_date)}"
        )
    else:
        add_result(
            results,
            "ERROR",
            "aktiv måned oppsummert",
            f"Mangler ett eller flere av month_id/label/buy_date: month_id={fmt(month_id)}, label={fmt(label)}, buy_date={fmt(buy_date)}"
        )

    # 5. Sjekk status
    status = active_month.get("status")
    if status == "active":
        add_result(results, "OK", "aktiv månedsstatus", "status=active")
    else:
        add_result(results, "WARN", "aktiv månedsstatus", f"Forventet active, fikk {fmt(status)}")

    # 6. Sjekk positions / picks
    month_positions = active_month.get("positions", [])
    current_positions = current_portfolio.get("positions", [])

    if len(month_positions) == 3:
        add_result(results, "OK", "månedspicks", "3 picks i månedsfil")
    else:
        add_result(results, "ERROR", "månedspicks", f"Forventet 3 picks, fikk {len(month_positions)}")

    if len(current_positions) == 3:
        add_result(results, "OK", "aktive picks", "3 picks i current_portfolio")
    else:
        add_result(results, "ERROR", "aktive picks", f"Forventet 3 picks, fikk {len(current_positions)}")

    month_tickers = [p.get("ticker") for p in month_positions]
    current_tickers = [p.get("ticker") for p in current_positions]
    compare_scalar(results, "tickers month vs current", current_tickers, month_tickers)

    # 7. Sjekk buy_price / current_price
    zero_buy_prices = []
    for p in current_positions:
        if p.get("buy_price") in (None, 0):
            zero_buy_prices.append(p.get("ticker"))

    if zero_buy_prices:
        add_result(results, "WARN", "buy_price aktive picks", f"Disse har buy_price=0/null: {', '.join(zero_buy_prices)}")
    else:
        add_result(results, "OK", "buy_price aktive picks", "Alle aktive picks har buy_price")

    # 8. Benchmarks
    sp500 = benchmarks.get("sp500", {})
    dnb = benchmarks.get("dnb_global_indeks", {})

    if sp500.get("buy_price") not in (None, 0):
        add_result(results, "OK", "SP500 buy_price", fmt(sp500.get("buy_price")))
    else:
        add_result(results, "ERROR", "SP500 buy_price", f"Ugyldig verdi: {fmt(sp500.get('buy_price'))}")

    if dnb.get("buy_nav") not in (None, 0):
        add_result(results, "OK", "DNB buy_nav", fmt(dnb.get("buy_nav")))
    else:
        add_result(results, "WARN", "DNB buy_nav", f"Ugyldig eller mangler: {fmt(dnb.get('buy_nav'))}")

    add_result(
        results,
        "INFO",
        "benchmark snapshot",
        f"SP500 buy={fmt(sp500.get('buy_price'))}, current={fmt(sp500.get('current_price'))}, return={fmt(sp500.get('return_pct'))}; "
        f"DNB buy={fmt(dnb.get('buy_nav'))}, current={fmt(dnb.get('current_nav'))}, return={fmt(dnb.get('return_pct'))}, as_of={fmt(dnb.get('as_of_date'))}"
    )

    # 9. Performance
    add_result(
        results,
        "INFO",
        "performance snapshot",
        f"portfolio_return_pct={fmt(performance.get('portfolio_return_pct'))}, "
        f"alpha_vs_sp500={fmt(performance.get('alpha_vs_sp500'))}, "
        f"alpha_vs_dnb={fmt(performance.get('alpha_vs_dnb'))}, "
        f"updated_at={fmt(performance.get('updated_at'))}"
    )

    # 10. Chart data
    series = chart_data.get("series", [])
    if isinstance(series, list):
        add_result(results, "OK", "chart_data.series", f"Antall punkter: {len(series)}")
    else:
        add_result(results, "ERROR", "chart_data.series", "series er ikke en liste")

    if series:
        first_point = series[0]
        last_point = series[-1]
        add_result(
            results,
            "INFO",
            "chart_data snapshot",
            f"første=({fmt(first_point.get('timestamp'))}, p={fmt(first_point.get('portfolio_return_pct'))}, s={fmt(first_point.get('sp500_return_pct'))}, d={fmt(first_point.get('dnb_return_pct'))}) | "
            f"siste=({fmt(last_point.get('timestamp'))}, p={fmt(last_point.get('portfolio_return_pct'))}, s={fmt(last_point.get('sp500_return_pct'))}, d={fmt(last_point.get('dnb_return_pct'))})"
        )

    # 11. Raw files for active month
    raw_portfolio = os.path.join(RAW_DIR, f"{active_month_id}-portfolio.txt")
    raw_midmonth = os.path.join(RAW_DIR, f"{active_month_id}-midmonth.txt")
    raw_month_end = os.path.join(RAW_DIR, f"{active_month_id}-month-end.txt")

    check_optional(results, raw_portfolio, "raw portfolio-fil")
    check_optional(results, raw_midmonth, "raw midmonth-fil")
    check_optional(results, raw_month_end, "raw month-end-fil")

    # 12. Midmonth / month_end presence
    if active_month.get("midmonth_update") is None:
        add_result(results, "INFO", "midmonth_update", "Ingen midmonth_update ennå")
    else:
        add_result(results, "OK", "midmonth_update", f"Finnes med dato {fmt(active_month['midmonth_update'].get('date'))}")

    if active_month.get("month_end") is None:
        add_result(results, "INFO", "month_end", "Ingen month_end ennå")
    else:
        add_result(results, "OK", "month_end", f"Finnes med dato {fmt(active_month['month_end'].get('date'))}")

    # 13. months index summary
    months = months_index.get("months", [])
    add_result(results, "INFO", "index.json måneder", f"Antall måneder i index: {len(months)}")

    # 14. held_positions summary
    held_portfolios = held_positions.get("portfolios", [])
    add_result(results, "INFO", "held_positions", f"Antall tracked porteføljer: {len(held_portfolios)}")

    # 15. monthly_history / track_record summary
    add_result(results, "INFO", "monthly_history", f"Antall historikk-rader: {len(monthly_history)}")
    add_result(
        results,
        "INFO",
        "track_record",
        f"months_completed={fmt(track_record.get('months_completed'))}, "
        f"beat_sp500_count={fmt(track_record.get('beat_sp500_count'))}, "
        f"beat_dnb_count={fmt(track_record.get('beat_dnb_count'))}, "
        f"cumulative_portfolio_return_pct={fmt(track_record.get('cumulative_portfolio_return_pct'))}"
    )

    print_report(results)


def compare_scalar(results: List[Tuple[str, str, str]], label: str, actual: Any, expected: Any) -> None:
    if actual == expected:
        add_result(results, "OK", label, f"{fmt(actual)}")
    else:
        add_result(results, "ERROR", label, f"faktisk={fmt(actual)} | forventet={fmt(expected)}")


def check_optional(results: List[Tuple[str, str, str]], path: str, label: str) -> None:
    if exists(path):
        add_result(results, "OK", label, path)
    else:
        add_result(results, "INFO", label, f"Finnes ikke ennå: {path}")


def print_report(results: List[Tuple[str, str, str]]) -> None:
    counts = {"OK": 0, "INFO": 0, "WARN": 0, "ERROR": 0}
    for level, _, _ in results:
        counts[level] = counts.get(level, 0) + 1

    print("=== LOCAL STATE AUDIT ===")
    print(f"OK: {counts['OK']} | INFO: {counts['INFO']} | WARN: {counts['WARN']} | ERROR: {counts['ERROR']}")
    print("")

    for level, label, detail in results:
        print(f"[{level}] {label}: {detail}")

    print("")
    print("=== END AUDIT ===")

    if counts["ERROR"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()