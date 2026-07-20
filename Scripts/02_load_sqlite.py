# Loads master_citypair.csv into SQLite (database/aviation.db) and builds indexes.

import sqlite3
from pathlib import Path
import pandas as pd

BASE     = Path(__file__).resolve().parent.parent
CSV_PATH = BASE / "data" / "cleaned" / "master_citypair.csv"
DB_PATH  = BASE / "database" / "aviation.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

print(f"Reading {CSV_PATH.name} ...")
df = pd.read_csv(CSV_PATH)
print(f"  -> {len(df):,} rows, columns: {list(df.columns)}")

print(f"\nWriting to {DB_PATH} ...")
con = sqlite3.connect(DB_PATH)

df.to_sql("citypair", con, if_exists="replace", index=False)
print("  -> Table 'citypair' created.")

cur = con.cursor()
indexes = [
    "CREATE INDEX IF NOT EXISTS idx_year       ON citypair(year)",
    "CREATE INDEX IF NOT EXISTS idx_route      ON citypair(route)",
    "CREATE INDEX IF NOT EXISTS idx_year_route ON citypair(year, route)",
    "CREATE INDEX IF NOT EXISTS idx_month      ON citypair(month)",
]
for sql in indexes:
    cur.execute(sql)
print("  -> Indexes created.")
con.commit()

print("\n-- Sanity Checks --------------------------------------------------")

checks = {
    "Total rows":
        "SELECT COUNT(*) AS total_rows FROM citypair",

    "Unique routes":
        "SELECT COUNT(DISTINCT route) AS unique_routes FROM citypair",

    "Year range":
        "SELECT MIN(year) AS from_year, MAX(year) AS to_year FROM citypair",

    "Rows per year":
        "SELECT year, COUNT(*) AS rows FROM citypair GROUP BY year ORDER BY year",

    "Top 5 routes by total passengers (all years)": """
        SELECT route, SUM(total_pax) AS total_passengers
        FROM citypair
        GROUP BY route
        ORDER BY total_passengers DESC
        LIMIT 5
    """,

    "Null check": """
        SELECT
            SUM(CASE WHEN route     IS NULL THEN 1 ELSE 0 END) AS null_route,
            SUM(CASE WHEN total_pax IS NULL THEN 1 ELSE 0 END) AS null_pax,
            SUM(CASE WHEN year      IS NULL THEN 1 ELSE 0 END) AS null_year
        FROM citypair
    """,
}

for label, sql in checks.items():
    print(f"\n{label}:")
    result = pd.read_sql_query(sql, con)
    print(result.to_string(index=False))

con.close()
print("\nDone - aviation.db is ready.")
print(f"Location: {DB_PATH}")
