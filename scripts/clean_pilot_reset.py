import json
import os
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONTHS_DIR = os.path.join(DATA_DIR, "months")

MONTHLY_HISTORY_PATH = os.path.join(DATA_DIR, "monthly_history.json")
TRACK_RECORD_PATH = os.path.join(DATA_DIR, "track_record.json")
HELD_POSITIONS_PATH = os.path.join(DATA_DIR, "held_positions.json")
CHART_DATA_PATH = os.path.join(DATA_DIR, "chart_data.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def run_step(cmd):
    print(f"\n[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n[STOPP] Kommando feilet: {' '.join(cmd)}")
        sys.exit(result.returncode)


def reset_month_file(month_id, new_label=None):
    month_path = os.path.join(MONTHS_DIR, f"{month_id}.json")
    if not os.path.exists(month_path):
        print(f"Mangler månedsfil: {month_path}")
        sys.exit(1)

    month = load_json(month_path)

    month["status"] = "active"
    month["midmonth_update"] = None
    month["month_end"] = None

    if new_label:
        month["label"] = new_label

    save_json(month_path, month)
    print(f"[OK] Vasket månedsfil: {month_path}")


def reset_monthly_history():
    save_json(MONTHLY_HISTORY_PATH, [])
    print(f"[OK] Nullstilte {MONTHLY_HISTORY_PATH}")


def reset_track_record():
    data = {
        "months_completed": 0,
        "beat_sp500_count": 0,
        "beat_dnb_count": 0,
        "avg_alpha_vs_sp500": 0,
        "avg_alpha_vs_dnb": 0,
        "cumulative_portfolio_return_pct": 0
    }
    save_json(TRACK_RECORD_PATH, data)
    print(f"[OK] Nullstilte {TRACK_RECORD_PATH}")


def reset_held_positions():
    save_json(HELD_POSITIONS_PATH, {"portfolios": []})
    print(f"[OK] Nullstilte {HELD_POSITIONS_PATH}")


def reset_chart_data(month_id):
    data = {
        "month_id": month_id,
        "series": [
            {
                "timestamp": None,
                "portfolio_return_pct": 0,
                "sp500_return_pct": 0,
                "dnb_return_pct": 0
            }
        ]
    }
    save_json(CHART_DATA_PATH, data)
    print(f"[OK] Nullstilte {CHART_DATA_PATH}")


def main():
    if len(sys.argv) < 2:
        print('Bruk: python3 scripts/clean_pilot_reset.py 2026-05 "Runde 1"')
        sys.exit(1)

    month_id = sys.argv[1]
    new_label = sys.argv[2] if len(sys.argv) >= 3 else None

    if not os.getenv("FINNHUB_API_KEY"):
        print("Mangler miljøvariabel: FINNHUB_API_KEY")
        sys.exit(1)

    print("=== CLEAN PILOT RESET ===")
    print(f"month_id: {month_id}")
    print(f"label: {new_label if new_label else '(behold eksisterende)'}")

    reset_month_file(month_id, new_label=new_label)
    reset_monthly_history()
    reset_track_record()
    reset_held_positions()
    reset_chart_data(month_id)

    run_step(["python3", os.path.join("scripts", "hydrate_month_benchmarks.py"), month_id])
    run_step(["python3", os.path.join("scripts", "finalize_month_start.py"), month_id])
    run_step(["python3", os.path.join("scripts", "rebuild_months_index.py")])
    run_step(["python3", os.path.join("scripts", "apply_month_to_active.py"), month_id])

    print("\n[Ferdig] Pilot-reset er fullført.")
    print("Neste steg:")
    print("1. Kjør: python3 scripts/audit_local_state.py")
    print("2. Test lokalt i nettleser")
    print("3. Commit og push hvis alt ser riktig ut")


if __name__ == "__main__":
    main()