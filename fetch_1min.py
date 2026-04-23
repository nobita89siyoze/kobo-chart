import requests
import pandas as pd
import os
import sys

API_KEY = os.environ["JQUANTS_API_KEY"]
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_1min(code, date):
    date_fmt = date.replace("-", "")
    url = "https://api.jquants.com/v2/equities/bars/minute"
    headers = {"x-api-key": API_KEY}
    params = {"code": code, "date": date_fmt}

    print(f"APIキー先頭4文字: {API_KEY[:4]}")  # デバッグ用
    print(f"URL: {url}")
    print(f"params: {params}")

    all_rows = []
    while True:
        r = requests.get(url, headers=headers, params=params)
        print(f"HTTPステータス: {r.status_code}")
        print(f"レスポンス: {r.text[:200]}")  # 最初の200文字
        r.raise_for_status()
        j = r.json()
        rows = j.get("bars_minute", [])
        all_rows.extend(rows)
        pk = j.get("pagination_key")
        if not pk:
            break
        params["pagination_key"] = pk

    if not all_rows:
        print(f"[WARNING] {code} ({date}): データなし")
        return

    df = pd.DataFrame(all_rows)
    df["DateTime"] = pd.to_datetime(df["DateTime"])

    base = df["DateTime"].dt.normalize()
    start = base + pd.Timedelta(hours=9)
    end   = base + pd.Timedelta(hours=15, minutes=30)
    df = df[(df["DateTime"] >= start) & (df["DateTime"] <= end)]
    df = df.sort_values("DateTime").reset_index(drop=True)

    path = f"{OUTPUT_DIR}/{code}_{date}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"→ {path} ({len(df)}本)")

def main():
    targets_str = sys.argv[1] if len(sys.argv) > 1 else ""
    targets = [t.split(",") for t in targets_str.split(";") if "," in t]
    for code, date in targets:
        print(f"取得中: {code} / {date}")
        fetch_1min(code.strip(), date.strip())

if __name__ == "__main__":
    main()
