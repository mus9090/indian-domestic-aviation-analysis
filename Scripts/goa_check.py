import pandas as pd
import os
from pathlib import Path

raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"

for fname in os.listdir(raw_dir):
    if fname.lower().endswith(".xlsx"):
        df = pd.read_excel(os.path.join(raw_dir, fname), header=2, engine="openpyxl")
        df.columns = [str(c).strip().upper() for c in df.columns]
        if "CITY 1" in df.columns and "CITY 2" in df.columns:
            # find any row where city1 or city2 contains "GOA" or "MOPA"
            mask = (
                df["CITY 1"].astype(str).str.upper().str.contains("GOA|MOPA", na=False) |
                df["CITY 2"].astype(str).str.upper().str.contains("GOA|MOPA", na=False)
            )
            matches = df[mask][["CITY 1", "CITY 2"]].drop_duplicates()
            if not matches.empty:
                print(f"\n{fname}")
                print(matches.to_string(index=False))