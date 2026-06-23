"""
Fetch live NAV history from mfapi.in for selected mutual fund schemes.

The script saves a raw CSV extract to data/raw/live_nav_mfapi.csv.
"""

import pandas as pd
from pathlib import Path
import requests

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

def fetch_scheme(scheme_name, scheme_code):
    """Fetch and flatten NAV data for one scheme."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    meta = data.get("meta", {})
    rows = []
    for row in data.get("data", []):
        rows.append({
            "scheme_name_input": scheme_name,
            "scheme_code": scheme_code,
            "fund_house": meta.get("fund_house"),
            "scheme_type": meta.get("scheme_type"),
            "scheme_category": meta.get("scheme_category"),
            "scheme_name_api": meta.get("scheme_name"),
            "date": row.get("date"),
            "nav": row.get("nav"),
        })
    return rows


def main():
    """Fetch all configured schemes and write the raw CSV output."""
    all_rows = []
    for scheme_name, scheme_code in schemes.items():
        rows = fetch_scheme(scheme_name, scheme_code)
        print(f"Fetched {len(rows)} rows for {scheme_name}")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_csv(RAW_DIR / "live_nav_mfapi.csv", index=False)
    print(f"Saved {len(df)} rows to {RAW_DIR / 'live_nav_mfapi.csv'}")


if __name__ == "__main__":
    main()
