import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONTHS_DIR = os.path.join(DATA_DIR, "months")

CURRENT_PORTFOLIO_PATH = os.path.join(DATA_DIR, "current_portfolio.json")
BENCHMARKS_PATH = os.path.join(DATA_DIR, "benchmarks.json")
PERFORMANCE_PATH = os.path.join(DATA_DIR, "performance.json")
MONTHLY_HISTORY_PATH = os.path.join(DATA_DIR, "monthly_history.json")
TRACK_RECORD_PATH = os.path.join(DATA_DIR, "track_record.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def calculate_track_record(history):
    months_completed = len(history)
    beat_sp500_count = sum(1 for item in history if item["alpha_vs_sp500"] > 0)
    beat_dnb_count = sum(1 for item in history if item["alpha_vs_dnb"] > 0)

    avg_alpha_vs_sp500 = (
        sum(item["alpha_vs_sp500"] for item in history) / months_completed
        if months_completed else 0
    )
    avg_alpha_vs_dnb = (
        sum(item["alpha_vs_dnb"] for item in history) / months_completed
        if months_completed else 0
    )
    cumulative_portfolio_return_pct = (
        sum(item["portfolio_return_pct"] for item in history)
        if months_completed else 0
    )

    return {
        "months_completed": months_completed,
        "beat_sp500_count": beat_sp500_count,
        "beat_dnb_count": beat_dnb_count,
        "avg_alpha_vs_sp500": round(avg_alpha_vs_sp500, 4),
        "avg_alpha_vs_dnb": round(avg_alpha_vs_dnb, 4),
        "cumulative_portfolio_return_pct": round(cumulative_portfolio_return_pct, 4)
    }


def main():
    portfolio = load_json(CURRENT_PORTFOLIO_PATH)
    benchmarks = load_json(BENCHMARKS_PATH)
    performance = load_json(PERFORMANCE_PATH)
    history = load_json(MONTHLY_HISTORY_PATH)

    end_date = datetime.utcnow().strftime("%Y-%m-%d")

    existing_month_ids = {item["month_id"] for item in history}
    if portfolio["month_id"] in existing_month_ids:
        print(f"Måneden {portfolio['month_id']} finnes allerede i historikken. Ingen endring gjort.")
        return

    completed_month = {
        "month_id": portfolio["month_id"],
        "label": portfolio["label"],
        "buy_date": portfolio["buy_date"],
        "end_date": end_date,
        "portfolio_return_pct": round(performance["portfolio_return_pct"], 4),
        "sp500_return_pct": round(benchmarks["sp500"]["return_pct"], 4),
        "dnb_global_indeks_return_pct": round(benchmarks["dnb_global_indeks"]["return_pct"], 4) if benchmarks["dnb_global_indeks"]["return_pct"] is not None else None,
        "alpha_vs_sp500": round(performance["alpha_vs_sp500"], 4),
        "alpha_vs_dnb": round(performance["alpha_vs_dnb"], 4) if performance["alpha_vs_dnb"] is not None else None
    }

    history.append(completed_month)
    history = sorted(history, key=lambda item: item["month_id"], reverse=True)

    track_record = calculate_track_record([
        {
            **item,
            "alpha_vs_dnb": item["alpha_vs_dnb"] if item["alpha_vs_dnb"] is not None else 0
        }
        for item in history
    ])

    month_file_path = os.path.join(MONTHS_DIR, f"{portfolio['month_id']}.json")
    if os.path.exists(month_file_path):
        month_file = load_json(month_file_path)
        month_file["status"] = "completed"
        save_json(month_file_path, month_file)

    save_json(MONTHLY_HISTORY_PATH, history)
    save_json(TRACK_RECORD_PATH, track_record)

    print(f"La til {portfolio['label']} i monthly_history.json")
    print("Oppdaterte track_record.json og satte månedsfil til completed")


if __name__ == "__main__":
    main()