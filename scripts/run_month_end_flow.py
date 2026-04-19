import os
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_step(cmd):
    print(f"\n[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n[STOPP] Kommando feilet: {' '.join(cmd)}")
        sys.exit(result.returncode)


def main():
    if len(sys.argv) != 2:
        print("Bruk: python3 scripts/run_month_end_flow.py 2026-05")
        sys.exit(1)

    month_id = sys.argv[1]

    if not os.getenv("FINNHUB_API_KEY"):
        print("Mangler miljøvariabel: FINNHUB_API_KEY")
        sys.exit(1)

    run_step(["python3", os.path.join("scripts", "parse_month_end_output.py"), month_id])
    run_step(["python3", os.path.join("scripts", "rebuild_months_index.py")])
    run_step(["python3", os.path.join("scripts", "apply_month_to_active.py"), month_id])
    run_step(["python3", os.path.join("scripts", "update_prices.py")])
    run_step(["python3", os.path.join("scripts", "rollover_month.py")])

    print("\n[Ferdig] Månedsslutt er lagt inn og måneden er bokført i historikk/track record.")


if __name__ == "__main__":
    main()