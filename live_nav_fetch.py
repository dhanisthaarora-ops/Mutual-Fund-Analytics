import requests
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

schemes = {
    "HDFC Top 100 Direct": "125497",
    "SBI Bluechip": "119551",
    "ICICI Bluechip": "120503",
    "Nippon Large Cap": "118632",
    "Axis Bluechip": "119092",
    "Kotak Bluechip": "120841",
}

all_rows = []

for scheme_name, scheme_code in schemes.items():
    url = f"https://api.mfapi.in/mf/{scheme_code}"

    response = requests.get(url)
    data = response.json()

    meta = data.get("meta", {})
    nav_data = data.get("data", [])

    for row in nav_data:
        all_rows.append({
            "scheme_name_input": scheme_name,
            "scheme_code": scheme_code,
            "fund_house": meta.get("fund_house"),
            "scheme_type": meta.get("scheme_type"),
            "scheme_category": meta.get("scheme_category"),
            "scheme_name_api": meta.get("scheme_name"),
            "date": row.get("date"),
            "nav": row.get("nav"),
        })

df = pd.DataFrame(all_rows)

df.to_csv("data/raw/live_nav_mfapi.csv", index=False)

print("Live NAV data saved to data/raw/live_nav_mfapi.csv")
print(df.shape)
print(df.head())

