import pandas as pd
import os
import re
from pathlib import Path

BASE       = Path(__file__).resolve().parent.parent
RAW_DIR    = BASE / "data" / "raw"
OUTPUT_DIR = BASE / "data" / "cleaned"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

month_map = {
    "JAN": "January", "FEB": "February", "MAR": "March",
    "APR": "April",   "MAY": "May",       "JUN": "June",
    "JUL": "July",    "AUG": "August",    "SEP": "September",
    "OCT": "October", "NOV": "November",  "DEC": "December",

    "JANUARY": "January", "FEBRUARY": "February", "MARCH": "March",
    "APRIL": "April",     "MAY": "May",            "JUNE": "June",
    "JULY": "July",       "AUGUST": "August",      "SEPTEMBER": "September",
    "OCTOBER": "October", "NOVEMBER": "November",  "DECEMBER": "December",

    # DGCA misspells these in some monthly filenames
    "FEBURUARY":  "February",
    "FEBUARY":    "February",
    "JANURAY":    "January",
    "DECEMEBER":  "December",
    "NOVEMEBER":  "November",
    "SEPTEMEBER": "September",
}


def extract_date(filename):
    """Returns (month_str, year_int) from a DGCA filename, e.g. ('July', 2021)."""
    stem = Path(filename).stem.upper()

    year_match = re.search(r'\b(20\d{2})\b', stem)
    if not year_match:
        raise ValueError(f"could not find year in filename: {filename}")
    year = int(year_match.group(1))

    month = None
    for key, val in month_map.items():
        if re.search(r'\b' + key + r'\b', stem):
            month = val
            break
    if not month:
        raise ValueError(f"could not find month in filename: {filename}")

    return month, year


def clean_file(filepath):
    filename = os.path.basename(filepath)
    month, year = extract_date(filename)
    print(f"  processing: {filename}  ->  {month} {year}")

    # some files have multiple sheets; pick the one matching month/year
    xls = pd.ExcelFile(filepath, engine="openpyxl")
    target_sheet = next(
        (s for s in xls.sheet_names
         if month[:3].upper() in s.upper() or str(year) in s),
        xls.sheet_names[0]
    )
    df = pd.read_excel(xls, sheet_name=target_sheet, header=2, engine="openpyxl")

    df.columns = [str(c).strip().upper().replace("\n", " ").replace("  ", " ")
                  for c in df.columns]

    col_map = {
        "S.NO."                    : "sno",
        "S.NO"                     : "sno",
        "CITY 1"                   : "city1",
        "CITY 2"                   : "city2",
        "PASSENGERS   TO CITY 2"   : "pax_to",
        "PASSENGERS   FROM CITY 2" : "pax_from",
        "PASSENGERS TO CITY 2"     : "pax_to",
        "PASSENGERS FROM CITY 2"   : "pax_from",
        "FREIGHT   TO CITY 2"      : "freight_to",
        "FREIGHT   FROM CITY 2"    : "freight_from",
        "FREIGHT TO CITY 2"        : "freight_to",
        "FREIGHT FROM CITY 2"      : "freight_from",
        "MAIL   TO CITY 2"         : "mail_to",
        "MAIL   FROM CITY 2"       : "mail_from",
        "MAIL TO CITY 2"           : "mail_to",
        "MAIL FROM CITY 2"         : "mail_from",
    }
    df.rename(columns=col_map, inplace=True)

    keep = ["city1", "city2", "pax_to", "pax_from"]
    df = df[[c for c in keep if c in df.columns]]

    # drop footer / summary rows
    df = df[df["city1"].notna()]
    df = df[~df["city1"].astype(str).str.upper().str.contains("TOTAL|SUB|PAGE|CITY")]

    def clean_city(val):
        if pd.isna(val):
            return None
        val = str(val).strip().upper()
        replacements = {
            "DEHRA DUN"                    : "DEHRADUN",
            "DABOLIM"                      : "GOA",
            "BANGALORE"                    : "BENGALURU",
            "TRIVANDRUM"                   : "THIRUVANANTHAPURAM",
            "ALLAHABAD"                    : "PRAYAGRAJ",
            "BOMBAY"                       : "MUMBAI",
            "CALCUTTA"                     : "KOLKATA",
            "MADRAS"                       : "CHENNAI",
            "RAJKOT INTERNATIONAL AIRPORT" : "RAJKOT",
            "AYODHYA INTERNATIONAL AIRPORT": "AYODHYA",
            "HINDON AIRPORT"               : "HINDON",
            "SHIVAMOGGA AIRPORT"           : "SHIVAMOGGA",
            "ALIGARH AIRPORT"              : "ALIGARH",
            "CHITRAKOOT AIRPORT"           : "CHITRAKOOT",
            "AZAMGARH AIRPORT"             : "AZAMGARH",
            "SHRAVASTI AIRPORT"            : "SHRAVASTI",
            "MORADABAD AIRPORT"            : "MORADABAD",
            "AMBIKAPUR AIRPORT"            : "AMBIKAPUR",
            "MOPA, GOA"                    : "MOPA",
            "PURNIA AIRPORT"               : "PURNEA",
            "AMRAVATI AIRPORT"             : "AMRAVATI",
            "DATIA AIRPORT"                : "DATIA",
            "RAJKOT INTERNATIONAL AIRP" : "RAJKOT",
            "AYODHYA INTERNATIONAL AI"  : "AYODHYA",
        }
        return replacements.get(val, val)

    df["city1"] = df["city1"].apply(clean_city)
    df["city2"] = df["city2"].apply(clean_city)

    def clean_num(val):
        if pd.isna(val):
            return 0
        s = str(val).strip().replace(",", "")
        if s in ["-", "", "nil", "NIL", "N/A"]:
            return 0
        try:
            return int(float(s))
        except ValueError:
            return 0

    df["pax_to"]   = df["pax_to"].apply(clean_num)
    df["pax_from"] = df["pax_from"].apply(clean_num)

    # alphabetical route key so DEL-BOM and BOM-DEL are treated as the same route
    df["route"] = df.apply(
        lambda r: "-".join(sorted([str(r["city1"]), str(r["city2"])])), axis=1
    )

    df["total_pax"] = df["pax_to"] + df["pax_from"]
    df["month"] = month
    df["year"]  = year

    df = df[df["total_pax"] > 0]
    df = df[df["city1"] != df["city2"]]  # e.g. GOA-GOA from DABOLIM+GOA both mapping to GOA

    df = df[["year", "month", "route", "pax_to", "pax_from", "total_pax"]]
    df.reset_index(drop=True, inplace=True)

    return df


all_dfs = []

xlsx_files = sorted([
    f for f in os.listdir(RAW_DIR)
    if f.lower().endswith(".xlsx") and "citypair" in f.lower().replace(" ", "").replace(",", "")
])

if not xlsx_files:
    print(f"no xlsx files found in {RAW_DIR}/ - put your downloaded DGCA files there")
else:
    print(f"found {len(xlsx_files)} files\n")
    for fname in xlsx_files:
        fpath = os.path.join(RAW_DIR, fname)
        try:
            df = clean_file(fpath)
            all_dfs.append(df)
            print(f"    -> {len(df)} routes loaded\n")
        except Exception as e:
            print(f"    error: {e}\n")

    if all_dfs:
        master = pd.concat(all_dfs, ignore_index=True)
        out_path = os.path.join(OUTPUT_DIR, "master_citypair.csv")
        master.to_csv(out_path, index=False)

        print("=" * 50)
        print(f"DONE - {len(master)} total rows")
        print(f"saved to: {out_path}")
        print(f"\nyears covered: {sorted(master['year'].unique())}")
        print(f"total routes:  {master['route'].nunique()}")
        print(f"\npreview:")
        print(master.head(10).to_string())
    else:
        print("no data loaded - check your files and try again")
