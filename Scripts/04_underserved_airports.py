# Pillar 2 - underserved airports: 2025 traffic vs 2011 Census population, pax per lakh population

import sqlite3
from pathlib import Path
import pandas as pd

BASE     = Path(__file__).resolve().parent.parent
DB_PATH  = BASE / "database" / "aviation.db"
POP_PATH = BASE / "data" / "lookup" / "airport_city_population.csv"
OUT_PATH = BASE / "data" / "cleaned" / "underserved_airports.csv"

con = sqlite3.connect(DB_PATH)

print("-- Loading 2025 traffic per city --------------------------------------")

city_pax = pd.read_sql_query("""
    SELECT city, SUM(total_pax) AS total_pax_2025, COUNT(DISTINCT route) AS routes_2025
    FROM (
        SELECT
            SUBSTR(route, 1, INSTR(route, '-') - 1) AS city,
            total_pax,
            route
        FROM citypair
        WHERE year = 2025

        UNION ALL

        SELECT
            SUBSTR(route, INSTR(route, '-') + 1) AS city,
            total_pax,
            route
        FROM citypair
        WHERE year = 2025
    )
    GROUP BY city
    ORDER BY total_pax_2025 DESC
""", con)

print(f"  -> {len(city_pax)} airport cities found in 2025 data")

print("\n-- Loading population data --------------------------------------------")
pop = pd.read_csv(POP_PATH)
pop["city"] = pop["city"].str.strip().str.upper()
print(f"  -> {len(pop)} cities in population lookup")

merged = pd.merge(city_pax, pop, on="city", how="left")

missing = merged[merged["population_2011"].isna()]
if len(missing) > 0:
    print(f"\n  {len(missing)} cities have no population data:")
    print(missing[["city", "total_pax_2025"]].to_string(index=False))

merged = merged[merged["population_2011"].notna()].copy()
print(f"\n  -> {len(merged)} cities matched with population data")

merged["population_lakhs"] = (merged["population_2011"] / 100000).round(2)
merged["pax_per_lakh"]     = (merged["total_pax_2025"] / merged["population_lakhs"]).round(0).astype(int)


def connectivity_label(row):
    ppl = row["pax_per_lakh"]
    if ppl >= 500000:
        return "Hub"
    if ppl >= 100000:
        return "Well Connected"
    if ppl >= 30000:
        return "Adequately Connected"
    if ppl >= 5000:
        return "Underserved"
    return "Critically Underserved"


significant = merged[merged["population_2011"] >= 300000].copy()
significant["connectivity_status"] = significant.apply(connectivity_label, axis=1)
significant = significant.sort_values("pax_per_lakh")

print("\n-- Connectivity Summary (cities > 3 lakh population) ------------------")
print(significant["connectivity_status"].value_counts().to_string())

print("\n-- Top 15 Most Underserved Cities --------------------------------------")
underserved = significant[
    significant["connectivity_status"].isin(["Critically Underserved", "Underserved"])
].sort_values("pax_per_lakh")
print(underserved[["city","population_2011","total_pax_2025","pax_per_lakh",
                    "routes_2025","connectivity_status"]].head(15).to_string(index=False))

print("\n-- Top 10 Best Connected Cities -----------------------------------------")
top = significant.sort_values("pax_per_lakh", ascending=False).head(10)
print(top[["city","population_2011","total_pax_2025","pax_per_lakh",
           "routes_2025","connectivity_status"]].to_string(index=False))

print("\n-- Full Distribution -----------------------------------------------------")
print(significant[["city","population_2011","total_pax_2025",
                    "pax_per_lakh","routes_2025","connectivity_status"]
                  ].sort_values("pax_per_lakh").to_string(index=False))

merged_out = merged[["city","population_2011","population_lakhs",
                      "total_pax_2025","routes_2025","pax_per_lakh"]].copy()
merged_out["connectivity_status"] = merged_out.apply(
    lambda r: connectivity_label(r) if r["population_2011"] >= 300000 else "Small Airport Town",
    axis=1
)
merged_out = merged_out.sort_values("pax_per_lakh")
merged_out.to_csv(OUT_PATH, index=False)
print(f"\nSaved -> {OUT_PATH}")
print(f"   {len(merged_out)} cities total")

con.close()
