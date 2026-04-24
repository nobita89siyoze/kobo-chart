import requests
import pandas as pd
import os
import sys
import json

API_KEY = os.environ["JQUANTS_API_KEY"]
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_1min(code, date):
    date_fmt = date.replace("-", "")
    url = "https://api.jquants.com/v2/equities/bars/minute"
    headers = {"x-api-key": API_KEY}
    params = {"code": code, "date": date_fmt}

    all_rows = []
    while True:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        j = r.json()
        rows = j.get("data", []) or j.get("bars_minute", [])
        all_rows.extend(rows)
        pk = j.get("pagination_key")
        if not pk:
            break
        params["pagination_key"] = pk

    if not all_rows:
        print(f"  [SKIP] {code} ({date}): データなし")
        return

    df = pd.DataFrame(all_rows)
    df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])

    base = df["DateTime"].dt.normalize()
    start = base + pd.Timedelta(hours=9)
    end   = base + pd.Timedelta(hours=15, minutes=30)
    df = df[(df["DateTime"] >= start) & (df["DateTime"] <= end)]
    df = df.sort_values("DateTime").reset_index(drop=True)

    path = f"{OUTPUT_DIR}/{code}_{date}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  → {path} ({len(df)}本)")

def main():
    year_filter = sys.argv[1] if len(sys.argv) > 1 else "all"

    with open("offering_stocks.json", encoding="utf-8") as f:
        stocks = json.load(f)

    # 年でフィルタ
    if year_filter != "all":
        stocks = [s for s in stocks if s["delivery_date"].startswith(year_filter)]

    print(f"対象: {len(stocks)}件 (year={year_filter})")

    for s in stocks:
        code = s["code"]
        date = s["delivery_date"]
        print(f"取得中: {code} / {date}")
        try:
            fetch_1min(code, date)
        except Exception as e:
            print(f"  [ERROR] {code} ({date}): {e}")

if __name__ == "__main__":
    main()
