import os
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


def run_step(cmd):
    print(f"\n[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n[STOPP] Kommando feilet: {' '.join(cmd)}")
        sys.exit(result.returncode)


def main():
    if len(sys.argv) != 2:
        print("Bruk: python3 scripts/run_new_month_flow.py 2026-05")
        sys.exit(1)

    month_id = sys.argv[1]

    required_env = ["FINNHUB_API_KEY"]
    for env_name in required_env:
        if not os.getenv(env_name):
            print(f"Mangler miljøvariabel: {env_name}")
            sys.exit(1)

    run_step(["python3", os.path.join("scripts", "parse_llm_output.py"), month_id])
    run_step(["python3", os.path.join("scripts", "hydrate_month_benchmarks.py"), month_id])
    run_step(["python3", os.path.join("scripts", "finalize_month_start.py"), month_id])
    run_step(["python3", os.path.join("scripts", "rebuild_months_index.py")])
    run_step(["python3", os.path.join("scripts", "apply_month_to_active.py"), month_id])

    print("\n[Ferdig] Ny måned er bygget og satt som aktiv.")
    print("Tips: For månedstart-test skal du stoppe her.")
    print("Hvis du senere vil simulere at tid har gått, kjør: python3 scripts/update_prices.py")


if __name__ == "__main__":
    main()