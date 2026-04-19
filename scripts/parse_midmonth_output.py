import json
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
MONTHS_DIR = os.path.join(DATA_DIR, "months")


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def extract_fill_block(text):
    marker = "DEL 2: UTFYLLINGSBLOKK FOR MÅNEDSFIL"
    if marker not in text:
        raise ValueError("Fant ikke DEL 2: UTFYLLINGSBLOKK FOR MÅNEDSFIL")
    return text.split(marker, 1)[1].strip()


def parse_key_values(block):
    data = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def get_required(data, key):
    if key not in data or not data[key]:
        raise ValueError(f"Mangler felt: {key}")
    return data[key]


def main():
    if len(sys.argv) != 2:
        print("Bruk: python3 scripts/parse_midmonth_output.py 2026-05")
        sys.exit(1)

    month_id = sys.argv[1]
    raw_path = os.path.join(RAW_DIR, f"{month_id}-midmonth.txt")
    month_path = os.path.join(MONTHS_DIR, f"{month_id}.json")

    text = read_text(raw_path)
    fill_block = extract_fill_block(text)
    fields = parse_key_values(fill_block)

    month = load_json(month_path)

    month["midmonth_update"] = {
        "date": get_required(fields, "midmonth_update.date"),
        "portfolio_status": get_required(fields, "midmonth_update.portfolio_status"),
        "hold_recommendation": get_required(fields, "midmonth_update.hold_recommendation"),
        "biggest_risk_rest_of_month": get_required(fields, "midmonth_update.biggest_risk_rest_of_month"),
        "summary": get_required(fields, "midmonth_update.summary"),
        "positions": [
            {
                "ticker": get_required(fields, "midmonth_update.position_1.ticker"),
                "thesis_status": get_required(fields, "midmonth_update.position_1.thesis_status"),
                "comment": get_required(fields, "midmonth_update.position_1.comment")
            },
            {
                "ticker": get_required(fields, "midmonth_update.position_2.ticker"),
                "thesis_status": get_required(fields, "midmonth_update.position_2.thesis_status"),
                "comment": get_required(fields, "midmonth_update.position_2.comment")
            },
            {
                "ticker": get_required(fields, "midmonth_update.position_3.ticker"),
                "thesis_status": get_required(fields, "midmonth_update.position_3.thesis_status"),
                "comment": get_required(fields, "midmonth_update.position_3.comment")
            }
        ]
    }

    save_json(month_path, month)
    print(f"Oppdaterte midmonth_update i {month_path}")


if __name__ == "__main__":
    main()