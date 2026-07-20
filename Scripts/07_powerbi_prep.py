# Cleans and re-exports all pillar CSVs to data/powerbi/ for a clean Power BI import

import re
from pathlib import Path
import pandas as pd

BASE     = Path(__file__).resolve().parent.parent
SRC_DIR  = BASE / "data" / "cleaned"
OUT_DIR  = BASE / "data" / "powerbi"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "master_citypair.csv",
    "covid_recovery.csv",
    "underserved_airports.csv",
    "seasonal_national.csv",
    "seasonal_airports.csv",
    "seasonal_routes.csv",
    "hhi_competition.csv",
    "hhi_operator_shares.csv",
]

# Manual coordinate overrides for cities Bing's map visual geocodes poorly or
# ambiguously (see dashboard/map_geocoding_check.md). Left blank for every
# other city, which still geocodes fine by name.
LATLONG_OVERRIDES = {
    "HINDON":     (28.7058, 77.3422),
    "RUPSI":      (26.1418, 89.9077),
    "TEZU":       (27.9421, 96.1347),
    "UTKELA":     (20.0974, 83.1838),
    "LILABARI":   (27.2957, 94.0973),
    "PASIGHAT":   (28.0648, 95.3370),
    "ZIRO":       (27.5883, 93.8281),
    "VIDYANAGAR": (15.1785, 76.6281),
    # ambiguous-name cities: pinned to the specific airport DGCA actually tracks,
    # not the generic city name Bing might resolve to
    "SALEM":      (11.7823, 78.0646),   # Salem Airport, Tamil Nadu (not Salem, US)
    "SRINAGAR":   (33.9872, 74.7742),   # Srinagar Airport, Kashmir (not Srinagar, Uttarakhand)
    "AURANGABAD": (19.8627, 75.3981),   # Aurangabad Airport, Maharashtra (not Aurangabad, Bihar)
    "BILASPUR":   (21.9946, 82.1146),   # Bilaspur Airport, Chhattisgarh (not Bilaspur, HP)
    "AMRAVATI":   (20.8141, 77.7211),   # Amravati (Belora) Airport, Maharashtra (not Amaravati, AP)
    "ADAMPUR":    (31.4338, 75.7588),   # Adampur Airport, Punjab
    "GOA":        (15.3806, 73.8311),   # Dabolim Airport (separate from MOPA, which is unambiguous)
}


def clean_column_name(col):
    col = col.strip().lower()
    col = re.sub(r"[^\w]+", "_", col)
    return col.strip("_")


for fname in FILES:
    src = SRC_DIR / fname
    if not src.exists():
        print(f"{fname}: MISSING at {src}")
        continue

    df = pd.read_csv(src)

    df.columns = [clean_column_name(c) for c in df.columns]

    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].str.strip()

    if fname == "underserved_airports.csv":
        df["latitude"]  = df["city"].map(lambda c: LATLONG_OVERRIDES.get(c, (None, None))[0])
        df["longitude"] = df["city"].map(lambda c: LATLONG_OVERRIDES.get(c, (None, None))[1])

    out_path = OUT_DIR / fname
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"{fname}: {df.shape[0]} rows, {df.shape[1]} cols -> {out_path}")

print(f"\nDone. Clean CSVs saved to {OUT_DIR}")
