import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CURRENT_PORTFOLIO_PATH = os.path.join(DATA_DIR, "current_portfolio.json")
BENCHMARKS_PATH = os.path.join(DATA_DIR, "benchmarks.json")
PERFORMANCE_PATH = os.path.join(DATA_DIR, "performance.json")
CHART_DATA_PATH = os.path.join(DATA_DIR, "chart_data.json")

API_KEY = os.getenv("FINNHUB_API_KEY")

DNB_FUND_URL = "https://www.dnb.no/sparing/fond/fond-liste/d/dnb-global-indeks-a-NO0010582984"
EURONEXT_FUND_URL = "https://live.euronext.com/nb/product/funds/NO0010582984.DKGLBIX-WOMF"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fetch_text(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "nb-NO,nb;q=0.9,en;q=0.8"
        },
    )
    with urlopen(request) as response:
        return response.read().decode("utf-8", errors="ignore")


def fetch_quote(symbol):
    params = urlencode({
        "symbol": symbol,
        "token": API_KEY,
    })
    url = f"https://finnhub.io/api/v1/quote?{params}"

    with urlopen(url) as response:
        raw = response.read().decode("utf-8")
        data = json.loads(raw)

    current_price = data.get("c")
    previous_close = data.get("pc")

    if current_price in (None, 0):
        raise ValueError(f"Ingen gyldig pris for {symbol}: {data}")

    return {
        "current_price": float(current_price),
        "previous_close": float(previous_close) if previous_close else None
    }


def normalize_number(value):
    value = value.replace("\xa0", " ").replace(" ", "")
    value = value.replace(",", ".")
    return float(value)


def try_fetch_dnb_nav_from_dnb():
    html = fetch_text(DNB_FUND_URL)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    pattern = r"NAV/Kurs\s+(?P<nav>\d+[.,]\d+)\s+kroner\s+(?P<date>\d{1,2}\.\s*[A-Za-zæøåÆØÅ]{3,}\.?\s*\d{4})"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        nav = normalize_number(match.group("nav"))
        date = match.group("date").strip()
        return {"nav": nav, "date": date, "source": "dnb.no"}

    anchor = re.search(r"NAV/Kurs", text, re.IGNORECASE)
    if anchor:
        snippet = text[anchor.start(): anchor.start() + 300]
        nav_match = re.search(r"(\d+[.,]\d+)\s+kroner", snippet, re.IGNORECASE)
        date_match = re.search(r"(\d{1,2}\.\s*[A-Za-zæøåÆØÅ]{3,}\.?\s*\d{4})", snippet, re.IGNORECASE)

        if nav_match and date_match:
            nav = normalize_number(nav_match.group(1))
            date = date_match.group(1).strip()
            return {"nav": nav, "date": date, "source": "dnb.no"}

    raise ValueError("Fant ikke NAV/Kurs på DNB-siden")


def try_fetch_dnb_nav_from_euronext():
    html = fetch_text(EURONEXT_FUND_URL)

    patterns = [
        r'"lastPrice"\s*:\s*"?(?P<nav>\d+[.,]\d+)"?',
        r'"price"\s*:\s*"?(?P<nav>\d+[.,]\d+)"?',
        r'"close"\s*:\s*"?(?P<nav>\d+[.,]\d+)"?',
        r'data-last-price\s*=\s*"(?P<nav>\d+[.,]\d+)"'
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            nav = normalize_number(match.group("nav"))
            return {"nav": nav, "date": None, "source": "euronext"}

    raise ValueError("Fant ikke pris/NAV på Euronext-siden")


def try_fetch_dnb_nav():
    errors = []

    try:
        return try_fetch_dnb_nav_from_dnb()
    except Exception as exc:
        errors.append(f"DNB-kilde feilet: {exc}")

    try:
        return try_fetch_dnb_nav_from_euronext()
    except Exception as exc:
        errors.append(f"Euronext-kilde feilet: {exc}")

    raise ValueError(" | ".join(errors))


def calculate_return_pct(buy_price, current_price):
    if buy_price in (None, 0):
        return None
    return ((current_price - buy_price) / buy_price) * 100


def calculate_portfolio_return(positions):
    valid = [p["return_pct"] for p in positions if p["return_pct"] is not None]
    if not valid:
        return 0.0
    return sum(valid) / len(valid)


def find_best_contributor(positions):
    valid = [p for p in positions if p["return_pct"] is not None]
    return max(valid, key=lambda p: p["return_pct"]) if valid else {"ticker": "", "return_pct": 0}


def find_worst_contributor(positions):
    valid = [p for p in positions if p["return_pct"] is not None]
    return min(valid, key=lambda p: p["return_pct"]) if valid else {"ticker": "", "return_pct": 0}


def append_chart_point(month_id, updated_at, portfolio_return, sp500_return, dnb_return):
    chart_data = load_json(CHART_DATA_PATH)

    if chart_data.get("month_id") != month_id:
        chart_data = {
            "month_id": month_id,
            "series": []
        }

    new_point = {
        "timestamp": updated_at,
        "portfolio_return_pct": portfolio_return,
        "sp500_return_pct": sp500_return,
        "dnb_return_pct": dnb_return
    }

    if chart_data["series"]:
        last_point = chart_data["series"][-1]
        if last_point.get("timestamp") == updated_at:
            chart_data["series"][-1] = new_point
        else:
            chart_data["series"].append(new_point)
    else:
        chart_data["series"].append(new_point)

    save_json(CHART_DATA_PATH, chart_data)


def main():
    if not API_KEY:
        print("FINNHUB_API_KEY mangler.")
        sys.exit(1)

    portfolio = load_json(CURRENT_PORTFOLIO_PATH)
    benchmarks = load_json(BENCHMARKS_PATH)
    performance = load_json(PERFORMANCE_PATH)

    updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    for position in portfolio["positions"]:
        symbol = position["ticker"]
        quote = fetch_quote(symbol)
        position["current_price"] = round(quote["current_price"], 4)
        position["return_pct"] = round(
            calculate_return_pct(position["buy_price"], position["current_price"]),
            4
        )

    sp500_symbol = benchmarks["sp500"]["proxy_ticker"]
    sp500_quote = fetch_quote(sp500_symbol)
    benchmarks["sp500"]["current_price"] = round(sp500_quote["current_price"], 4)
    benchmarks["sp500"]["return_pct"] = round(
        calculate_return_pct(
            benchmarks["sp500"]["buy_price"],
            benchmarks["sp500"]["current_price"]
        ),
        4
    )

    if benchmarks["dnb_global_indeks"]["buy_nav"] not in (None, 0):
        try:
            dnb_data = try_fetch_dnb_nav()
            benchmarks["dnb_global_indeks"]["current_nav"] = round(dnb_data["nav"], 4)
            benchmarks["dnb_global_indeks"]["return_pct"] = round(
                calculate_return_pct(
                    benchmarks["dnb_global_indeks"]["buy_nav"],
                    benchmarks["dnb_global_indeks"]["current_nav"]
                ),
                4
            )
            if dnb_data["date"]:
                benchmarks["dnb_global_indeks"]["as_of_date"] = dnb_data["date"]
        except Exception as exc:
            print(f"Advarsel: klarte ikke å oppdatere DNB Global Indeks: {exc}")

    portfolio_return = round(calculate_portfolio_return(portfolio["positions"]), 4)
    alpha_vs_sp500 = round(portfolio_return - benchmarks["sp500"]["return_pct"], 4)

    dnb_return = benchmarks["dnb_global_indeks"]["return_pct"]
    alpha_vs_dnb = round(portfolio_return - dnb_return, 4) if dnb_return is not None else None

    best = find_best_contributor(portfolio["positions"])
    worst = find_worst_contributor(portfolio["positions"])

    performance["month_id"] = portfolio["month_id"]
    performance["updated_at"] = updated_at
    performance["portfolio_return_pct"] = portfolio_return
    performance["alpha_vs_sp500"] = alpha_vs_sp500
    performance["alpha_vs_dnb"] = alpha_vs_dnb
    performance["best_contributor"] = {
        "ticker": best["ticker"],
        "return_pct": round(best["return_pct"], 4) if best["return_pct"] is not None else 0
    }
    performance["worst_contributor"] = {
        "ticker": worst["ticker"],
        "return_pct": round(worst["return_pct"], 4) if worst["return_pct"] is not None else 0
    }

    portfolio["updated_at"] = updated_at
    benchmarks["updated_at"] = updated_at

    save_json(CURRENT_PORTFOLIO_PATH, portfolio)
    save_json(BENCHMARKS_PATH, benchmarks)
    save_json(PERFORMANCE_PATH, performance)

    append_chart_point(
        portfolio["month_id"],
        updated_at,
        portfolio_return,
        benchmarks["sp500"]["return_pct"],
        dnb_return
    )

    print("Oppdaterte priser, benchmarks, performance og chart_data.")
    print(f"updated_at={updated_at}")


if __name__ == "__main__":
    main()