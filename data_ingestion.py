import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")

csv_files = list(RAW_DIR.glob("*.csv"))

if not csv_files:
    print("No CSV files found in data/raw. Please add your 10 CSV files there.")

for file in csv_files:
    print("\n==============================")
    print(f"File: {file.name}")

    df = pd.read_csv(file)

    print("Shape:")
    print(df.shape)

    print("\nDtypes:")
    print(df.dtypes)

    print("\nHead:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

