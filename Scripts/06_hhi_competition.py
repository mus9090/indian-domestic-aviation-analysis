# Pillar 4 - HHI per route from DGCA Summer 2026 flight-schedule frequency (proxy for market share)
# HHI = sum(operator share of weekly flights ^2) * 10000; single operator = Monopoly (10000)

import pdfplumber
import pandas as pd
from pathlib import Path

BASE     = Path(__file__).resolve().parent.parent
PDF_DIR  = BASE / "data" / "lookup" / "flight_schedule"
OUT_HHI  = BASE / "data" / "cleaned" / "hhi_competition.csv"
OUT_SHR  = BASE / "data" / "cleaned" / "hhi_operator_shares.csv"

FILE_TO_OPERATOR = {
    "AirIndiaExpressLimited_SS_2026.pdf": "Air India Express",
    "AirIndiaLtd_SS_2026.pdf": "Air India",
    "AllianceAir_SS_2026.pdf": "Alliance Air",
    "GSECMonarchandDeccanAviationPrivateLimited_SS_2026.pdf": "GSEC Monarch & Deccan Aviation",
    "Ghodawat EnterprisesPvtLtd_SS_2026.pdf": "Ghodawat Enterprises (Fly91)",
    "INTERGLOBE AVIATION LTD_2026.pdf": "IndiGo",
    "JUSTUDOAVIATIONPVTLTD_SS_2026.pdf": "JustUdo Aviation (IndiaOne Air)",
    "SNVAviation Private Limited_SS_2026.pdf": "Akasa Air",
    "SpiceJet_SS_2026.pdf": "SpiceJet",
}

# IATA/DGCA station code -> city name, reverse-engineered from the schedule data itself
RAW_CODE_TO_CITY = {
    "AGR": "Agra", "AGX": "Agatti", "AHA": "Ambikapur", "AIP": "Jalandhar",
    "AJL": "Aizawl", "AMD": "Ahmedabad", "ATQ": "Amritsar", "AVR": "Amravati",
    "AYJ": "Ayodhya", "BBI": "Bhubneshwar", "BDQ": "Vadodara", "BEK": "Bareilly",
    "BHJ": "Bhuj", "BHO": "Bhopal", "BHU": "Bhavnagar", "BKB": "Bikaner",
    "BLR": "Bangalore", "BOM": "Mumbai", "BUP": "Bathinda", "CCJ": "Kozhikode",
    "CCU": "Kolkata", "CDP": "Cuddapah", "CJB": "Coimbatore", "CNN": "Kannur",
    "COH": "Cooch Behar", "COK": "Kochi", "DBR": "Darbhanga", "DED": "Dehradun",
    "DEL": "Delhi", "DGH": "Deogarh", "DHM": "Dharamsala", "DIB": "Dibrugarh",
    "DIU": "Diu", "DMU": "Dimapur", "GAU": "Guwahati", "GAY": "Gaya",
    "GDB": "Gondia", "GOI": "Goa", "GOP": "Gorakhpur", "GOX": "GOA MOPA",
    "GWL": "Gwalior", "HBX": "Hubali", "HDO": "Hindon", "HGI": "Hollongi",
    "HJR": "Khajuraho", "HSR": "Rajkot", "HSS": "Hisar", "HWR": "Halwara",
    "HYD": "Hyderabad", "IDR": "Indore", "IMF": "Imphal", "ISK": "Nashik",
    "IXA": "Agartala", "IXB": "Bagdogra", "IXC": "Chandigarh", "IXD": "Prayagraj",
    "IXE": "Mangalore", "IXG": "Belgaum", "IXI": "Lilabari", "IXJ": "Jammu",
    "IXK": "Keshod", "IXL": "Leh", "IXM": "Madurai", "IXR": "Ranchi",
    "IXS": "Silchar", "IXT": "Passighat", "IXU": "Aurangabad", "IXW": "Jamshedpur",
    "IXX": "Bidar", "IXY": "Kandla", "IXZ": "Port Blair", "JAI": "Jaipur",
    "JDH": "Jodhpur", "JGA": "Jamnagar", "JGB": "Jagdalpur", "JLG": "Jalgaon",
    "JLR": "Jabalpur", "JRG": "Jharsuguda", "JRH": "Jorhat", "KJB": "Kurnool",
    "KLH": "Kolhapur", "KNU": "Kanpur", "KQH": "Kishangarh", "KUU": "Kullu",
    "LKO": "Lucknow", "MAA": "Chennai", "MYQ": "Mysore", "NAG": "Nagpur",
    "NDC": "Nanded", "NMI": "Navi Mumbai", "NNS": "Pithoragarh", "PAB": "Bilaspur",
    "PAT": "Patna", "PBD": "Porbandar", "PGH": "Pantnagar", "PNQ": "Pune",
    "PNY": "Pondicherry", "PXN": "Purnia", "PYB": "Jeypore", "RDP": "Durgapur",
    "REW": "Rewa", "RJA": "Rajahmundry", "RPR": "Raipur", "RQY": "Shivamogga",
    "RRK": "Raurkela", "RUP": "Rupsi", "SAG": "Shirdi", "SDW": "Sindhudurg",
    "SHL": "Shillong", "SLV": "Shimla", "SSE": "Solapur", "STV": "Surat",
    "SXR": "Srinagar", "SXV": "Salem", "TCR": "Tuticorin", "TEI": "Tezu",
    "TIR": "Tirupati", "TRV": "Trivandrum", "TRZ": "Trichy", "UDR": "Udaipur",
    "UKE": "Utkela", "VDY": "Vidyanagar", "VGA": "Vijayawada", "VNS": "Varanasi",
    "VTZ": "Vizag", "ZER": "Ziro",
}

# City-name standardisation to match master_citypair.csv conventions
RENAME = {
    "BANGALORE": "BENGALURU",
    "BHUBNESHWAR": "BHUBANESWAR",
    "HUBALI": "HUBLI",
    "HISAR": "HISSAR",
    "NASHIK": "NASIK",
    "BATHINDA": "BHATINDA",
    "GOA MOPA": "MOPA",
    "HOLLONGI": "ITANAGAR",
    "PASSIGHAT": "PASIGHAT",
    "RAURKELA": "ROURKELA",
    "SHIMLA": "SIMLA",
    "SOLAPUR": "SHOLAPUR",
    "TRIVANDRUM": "THIRUVANANTHAPURAM",
    "TRICHY": "TIRUCHIRAPALLY",
    "VIZAG": "VISAKHAPATNAM",
    "DEOGARH": "DEOGHAR",
    "PURNIA": "PURNEA",
    "HALWARA": "LUDHIANA",
    "AGATTI": "AGATTI ISLAND",
}


def standardize(name: str) -> str:
    name = name.upper().strip()
    return RENAME.get(name, name)


IATA_TO_CITY = {code: standardize(city) for code, city in RAW_CODE_TO_CITY.items()}

SEASON_WEEKS = 30  # length of the DGCA Summer 2026 season, for the avg weekly frequency figure
DATE_FMT = "%d/%m/%Y"


def parse_schedule(pdf_path: Path) -> list[dict]:
    operator = FILE_TO_OPERATOR[pdf_path.name]
    legs = []
    current_station = None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    if row[0] is None or row[0] == "Sl. No":
                        continue
                    if all(c is None for c in row[1:]):
                        current_station = row[0].strip()
                        continue
                    (_, _, _, _, frequency, _, _,
                     departure_to, _, effective_from, effective_to) = row
                    departure_to = (departure_to or "").strip()
                    if not departure_to:
                        continue  # arrival-leg row; the matching departure row covers this leg
                    if departure_to not in IATA_TO_CITY:
                        continue
                    origin = standardize(current_station)
                    dest = IATA_TO_CITY[departure_to]
                    if origin == dest:
                        continue
                    weekly_freq = len(frequency.strip())
                    if weekly_freq == 0:
                        continue
                    days = (pd.to_datetime(effective_to, format=DATE_FMT)
                            - pd.to_datetime(effective_from, format=DATE_FMT)).days
                    weeks = max(days, 1) / 7  # a same-day effective range still flew at least once
                    route = "-".join(sorted([origin, dest]))
                    legs.append({
                        "route": route,
                        "operator": operator,
                        "flights_in_season": weekly_freq * weeks,
                    })
    return legs


print("-- Parsing flight schedule PDFs ----------------------------------------")
all_legs = []
for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
    legs = parse_schedule(pdf_path)
    print(f"  {pdf_path.name:<55} {len(legs):>5} legs")
    all_legs.extend(legs)

legs_df = pd.DataFrame(all_legs)
print(f"\nTotal directed legs parsed: {len(legs_df)}")

shares = (legs_df.groupby(["route", "operator"])["flights_in_season"]
          .sum().reset_index())

route_totals = shares.groupby("route")["flights_in_season"].sum().rename("route_total")
shares = shares.merge(route_totals, on="route")
shares["share_pct"] = (shares["flights_in_season"] / shares["route_total"] * 100).round(2)
shares = shares.sort_values(["route", "share_pct"], ascending=[True, False]).reset_index(drop=True)


def hhi_group(g):
    hhi = ((g["share_pct"] / 100) ** 2).sum() * 10000
    top = g.iloc[0]
    return pd.Series({
        "num_operators": g["operator"].nunique(),
        "total_flights_season": round(g["flights_in_season"].sum(), 1),
        "avg_weekly_frequency": round(g["flights_in_season"].sum() / SEASON_WEEKS, 1),
        "hhi": round(hhi, 1),
        "top_operator": top["operator"],
        "top_operator_share_pct": top["share_pct"],
    })


hhi = shares.groupby("route").apply(hhi_group, include_groups=False).reset_index()


def market_structure(row):
    if row["num_operators"] == 1:
        return "Monopoly"
    if row["hhi"] >= 2500:
        return "Highly Concentrated"
    if row["hhi"] >= 1500:
        return "Moderately Concentrated"
    return "Competitive"


hhi["market_structure"] = hhi.apply(market_structure, axis=1)
hhi = hhi.sort_values("hhi", ascending=False).reset_index(drop=True)

print("\n-- Market Structure Summary ---------------------------------------------")
print(hhi["market_structure"].value_counts().to_string())
print(f"\nTotal routes: {len(hhi)}")

print("\n-- Top 10 Monopoly / Highly Concentrated Routes (by season volume) ------")
top_monopoly = hhi[hhi["market_structure"].isin(["Monopoly", "Highly Concentrated"])]
top_monopoly = top_monopoly.sort_values("total_flights_season", ascending=False).head(10)
print(top_monopoly[["route", "num_operators", "top_operator",
                     "top_operator_share_pct", "avg_weekly_frequency", "hhi"]].to_string(index=False))

print("\n── Competitive Routes (HHI < 1500) ──────────────────────────────────")
competitive_count = len(hhi[hhi["market_structure"] == "Competitive"])
if competitive_count == 0:
    print("No competitive routes found in the domestic network.")
    print("By HHI standards, every route is either a monopoly or highly concentrated.")
    print("\nLowest HHI route (closest to competitive):")
    print(hhi.sort_values("hhi").head(1)[
        ["route","num_operators","hhi","top_operator",
         "top_operator_share_pct","market_structure"]].to_string(index=False))
else:
    top_competitive = hhi[hhi["market_structure"] == "Competitive"]
    top_competitive = top_competitive.sort_values(
        "total_flights_season", ascending=False).head(10)
    print(top_competitive[["route","num_operators",
                           "avg_weekly_frequency","hhi"]].to_string(index=False))

hhi.to_csv(OUT_HHI, index=False)
shares.to_csv(OUT_SHR, index=False)
print(f"\nSaved -> {OUT_HHI}")
print(f"Saved -> {OUT_SHR}")
print(f"\nColumns (hhi_competition.csv): {list(hhi.columns)}")
print(f"Columns (hhi_operator_shares.csv): {list(shares.columns)}")
