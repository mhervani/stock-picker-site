import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTHS_DIR = os.path.join(BASE_DIR, "data", "months")
INDEX_PATH = os.path.join(MONTHS_DIR, "index.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    month_entries = []

    for filename in os.listdir(MONTHS_DIR):
        if not filename.endswith(".json"):
            continue
        if filename == "index.json":
            continue

        path = os.path.join(MONTHS_DIR, filename)
        data = load_json(path)

        month_id = data.get("month_id")
        label = data.get("label")
        status = data.get("status", "completed")

        if not month_id or not label:
            print(f"Skipper {filename}: mangler month_id eller label")
            continue

        month_entries.append({
            "month_id": month_id,
            "label": label,
            "status": status
        })

    month_entries.sort(key=lambda x: x["month_id"], reverse=True)

    active_month = None
    for entry in month_entries:
        if entry["status"] == "active":
            active_month = entry["month_id"]
            break

    if active_month is None and month_entries:
        active_month = month_entries[0]["month_id"]

    index_data = {
        "active_month": active_month,
        "months": month_entries
    }

    save_json(INDEX_PATH, index_data)
    print(f"Oppdaterte {INDEX_PATH}")


if __name__ == "__main__":
    main()