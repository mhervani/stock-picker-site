import json
import os
import re
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
MONTHS_DIR = os.path.join(DATA_DIR, "months")


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
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


def split_catalysts(value):
    return [item.strip() for item in value.split("|") if item.strip()]


def parse_ranking(value):
    return [item.strip() for item in value.split("|") if item.strip()]


def get_required(data, key):
    if key not in data or not data[key]:
        raise ValueError(f"Mangler felt: {key}")
    return data[key]


def to_float(value):
    return float(str(value).replace(",", "."))


def to_int(value):
    return int(float(str(value).replace(",", ".")))


def build_month_json(fields):
    month_id = get_required(fields, "month_id")
    label = get_required(fields, "label")
    buy_date = get_required(fields, "buy_date")
    analysis_date = get_required(fields, "analysis_date")

    positions = []
    for i in range(1, 4):
        positions.append({
            "ticker": get_required(fields, f"position_{i}.ticker"),
            "company": get_required(fields, f"position_{i}.company"),
            "exchange": get_required(fields, f"position_{i}.exchange"),
            "country": get_required(fields, f"position_{i}.country"),
            "sector": get_required(fields, f"position_{i}.sector"),
            "buy_price": 0,
            "weight": 0.333,
            "thesis": get_required(fields, f"position_{i}.thesis"),
            "catalysts": split_catalysts(get_required(fields, f"position_{i}.catalysts")),
            "risk": get_required(fields, f"position_{i}.risk"),
            "confidence": to_int(get_required(fields, f"position_{i}.confidence"))
        })

    return {
        "month_id": month_id,
        "label": label,
        "status": "active",
        "buy_date": buy_date,
        "analysis_date": analysis_date,
        "raw_source_file": f"{month_id}-portfolio.txt",
        "benchmarks": {
            "primary": "S&P 500",
            "secondary": "DNB Global Indeks",
            "sp500_proxy_ticker": "SPY",
            "sp500_buy_price": None,
            "dnb_global_indeks_buy_nav": None,
            "dnb_global_indeks_as_of_date": buy_date
        },
        "market_context": {
            "summary": get_required(fields, "market_context.summary"),
            "freshness_note": get_required(fields, "market_context.freshness_note"),
            "portfolio_conclusion": get_required(fields, "market_context.portfolio_conclusion"),
            "portfolio_confidence": to_float(get_required(fields, "market_context.portfolio_confidence"))
        },
        "portfolio": {
            "ranking": parse_ranking(get_required(fields, "portfolio.ranking")),
            "why_this_portfolio_can_win": get_required(fields, "portfolio.why_this_portfolio_can_win"),
            "biggest_portfolio_risk": get_required(fields, "portfolio.biggest_portfolio_risk")
        },
        "positions": positions,
        "midmonth_update": None,
        "month_end": None
    }


def main():
    if len(sys.argv) != 2:
        print("Bruk: python3 scripts/parse_llm_output.py 2026-05")
        sys.exit(1)

    month_id = sys.argv[1]
    raw_path = os.path.join(RAW_DIR, f"{month_id}-portfolio.txt")
    month_path = os.path.join(MONTHS_DIR, f"{month_id}.json")

    text = read_text(raw_path)
    fill_block = extract_fill_block(text)
    fields = parse_key_values(fill_block)
    data = build_month_json(fields)

    save_json(month_path, data)
    print(f"Laget {month_path}")


if __name__ == "__main__":
    main()