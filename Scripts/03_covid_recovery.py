# Pillar 1 - COVID recovery: recovery index per route = 2025 pax / 2019 pax * 100

import sqlite3
import pandas as pd
from pathlib import Path

BASE     = Path(__file__).resolve().parent.parent
DB_PATH  = BASE / "database" / "aviation.db"
OUT_PATH = BASE / "data" / "cleaned" / "covid_recovery.csv"

con = sqlite3.connect(DB_PATH)

print("-- National Trend --------------------------------------------------")
national = pd.read_sql_query("""
    SELECT
        year,
        SUM(total_pax) AS total_passengers,
        COUNT(DISTINCT route) AS active_routes
    FROM citypair
    GROUP BY year
    ORDER BY year
""", con)

national["pax_2019"] = national.loc[national["year"] == 2019, "total_passengers"].values[0]
national["recovery_pct"] = (national["total_passengers"] / national["pax_2019"] * 100).round(1)
print(national.to_string(index=False))

pax_2019 = pd.read_sql_query("""
    SELECT route, SUM(total_pax) AS pax_2019
    FROM citypair
    WHERE year = 2019
    GROUP BY route
    HAVING SUM(total_pax) >= 10000
""", con)

pax_2025 = pd.read_sql_query("""
    SELECT route, SUM(total_pax) AS pax_2025
    FROM citypair
    WHERE year = 2025
    GROUP BY route
""", con)

recovery = pd.merge(pax_2019, pax_2025, on="route", how="outer")


def recovery_index(row):
    if pd.isna(row["pax_2019"]) or row["pax_2019"] == 0:
        return None          # new route, no 2019 baseline
    if pd.isna(row["pax_2025"]) or row["pax_2025"] == 0:
        return 0             # lost route
    return round((row["pax_2025"] / row["pax_2019"]) * 100, 1)


recovery["recovery_index"] = recovery.apply(recovery_index, axis=1)


def status_label(row):
    if pd.isna(row["pax_2019"]) or row["pax_2019"] == 0:
        return "New Route"
    if pd.isna(row["pax_2025"]) or row["pax_2025"] == 0:
        return "Lost Route"
    if row["recovery_index"] >= 110:
        return "Fully Recovered & Grown"
    if row["recovery_index"] >= 90:
        return "Recovered"
    if row["recovery_index"] >= 50:
        return "Partially Recovered"
    return "Critically Lagging"


recovery["status"] = recovery.apply(status_label, axis=1)

recovery["pax_2019"] = recovery["pax_2019"].fillna(0).astype(int)
recovery["pax_2025"] = recovery["pax_2025"].fillna(0).astype(int)
recovery["pax_change"] = recovery["pax_2025"] - recovery["pax_2019"]

recovery = recovery.sort_values("recovery_index", ascending=False, na_position="last")
recovery = recovery.reset_index(drop=True)

print("\n-- Recovery Summary --------------------------------------------------")
summary = recovery["status"].value_counts()
print(summary.to_string())

print("\n-- Top 10 Most Recovered Routes --------------------------------------")
top10 = recovery[recovery["status"].isin([
    "Fully Recovered & Grown", "Recovered"
])].head(10)
print(top10[["route", "pax_2019", "pax_2025", "recovery_index", "status"]].to_string(index=False))

print("\n-- Top 10 Most Lagging Routes (had good 2019 traffic) ----------------")
lagging = recovery[
    (recovery["status"] == "Critically Lagging") &
    (recovery["pax_2019"] > 50000)
].sort_values("recovery_index").head(10)
print(lagging[["route", "pax_2019", "pax_2025", "recovery_index", "status"]].to_string(index=False))

print("\n-- Lost Routes (operated in 2019, gone by 2025) ----------------------")
lost = recovery[recovery["status"] == "Lost Route"]
print(f"  {len(lost)} routes lost")
print(lost[["route", "pax_2019"]].to_string(index=False))

print("\n-- New Routes (not in 2019, operating in 2025) -----------------------")
new_routes = recovery[recovery["status"] == "New Route"]
print(f"  {len(new_routes)} new routes")
print(new_routes[["route", "pax_2025"]].sort_values("pax_2025", ascending=False).to_string(index=False))

recovery.to_csv(OUT_PATH, index=False)
print(f"\nSaved -> {OUT_PATH}")
print(f"   {len(recovery)} routes total")

con.close()
