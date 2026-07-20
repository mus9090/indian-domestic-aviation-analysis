# Pillar 3 - seasonal patterns: monthly trends, airport/route seasonality index, peak months

import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

BASE     = Path(__file__).resolve().parent.parent
DB_PATH  = BASE / "database" / "aviation.db"
OUT1     = BASE / "data" / "cleaned" / "seasonal_national.csv"
OUT2     = BASE / "data" / "cleaned" / "seasonal_airports.csv"
OUT3     = BASE / "data" / "cleaned" / "seasonal_routes.csv"

con = sqlite3.connect(DB_PATH)

MONTH_ORDER = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]

print("-- Section 1: National Monthly Traffic --------------------------------")

national_monthly = pd.read_sql_query("""
    SELECT year, month, SUM(total_pax) AS total_pax
    FROM citypair
    GROUP BY year, month
    ORDER BY year
""", con)

national_monthly["month_num"] = national_monthly["month"].apply(
    lambda m: MONTH_ORDER.index(m) + 1 if m in MONTH_ORDER else 0
)
national_monthly = national_monthly.sort_values(["year","month_num"])

pivot = national_monthly.pivot(index="month", columns="year", values="total_pax")
pivot = pivot.reindex(MONTH_ORDER).dropna(how="all")
pivot_cr = (pivot / 1e7).round(2)

print("\nMonthly passengers by year (Crore):")
print(pivot_cr.to_string())

print("\nPeak month per year:")
for year in sorted(national_monthly["year"].unique()):
    yr_data = national_monthly[national_monthly["year"] == year]
    peak = yr_data.loc[yr_data["total_pax"].idxmax()]
    print(f"  {year}: {peak['month']} ({peak['total_pax']:,.0f} pax)")

pre_covid  = national_monthly[national_monthly["year"].isin([2019])]
post_covid = national_monthly[national_monthly["year"].isin([2023,2024])]

pre_avg  = pre_covid.groupby("month")["total_pax"].mean().reindex(MONTH_ORDER)
post_avg = post_covid.groupby("month")["total_pax"].mean().reindex(MONTH_ORDER)

print("\nPre-COVID (2019) vs Post-COVID (2023-24) monthly share (%):")
pre_share  = (pre_avg  / pre_avg.sum()  * 100).round(1)
post_share = (post_avg / post_avg.sum() * 100).round(1)
shift = (post_share - pre_share).round(1)
comparison = pd.DataFrame({
    "2019 share%"    : pre_share,
    "2023-24 share%" : post_share,
    "shift"          : shift
})
print(comparison.to_string())

print("\n-- Section 2: Airport Seasonality Index -------------------------------")
print("Higher index = more seasonal, lower = more stable year-round\n")

city_monthly = pd.read_sql_query("""
    SELECT city, month, SUM(total_pax) AS pax
    FROM (
        SELECT SUBSTR(route, 1, INSTR(route,'-')-1) AS city,
               month, total_pax FROM citypair WHERE year IN (2023,2024)
        UNION ALL
        SELECT SUBSTR(route, INSTR(route,'-')+1) AS city,
               month, total_pax FROM citypair WHERE year IN (2023,2024)
    )
    GROUP BY city, month
""", con)

seasonality = city_monthly.groupby("city")["pax"].agg(
    max_pax="max", min_pax="min", avg_pax="mean", total_pax="sum"
).reset_index()
seasonality["seasonality_index"] = (
    (seasonality["max_pax"] - seasonality["min_pax"]) / seasonality["avg_pax"] * 100
).round(1)

peak_month = city_monthly.loc[city_monthly.groupby("city")["pax"].idxmax()][["city","month"]]
peak_month.columns = ["city","peak_month"]
seasonality = pd.merge(seasonality, peak_month, on="city")

# keep only cities with data for most months (at least 8)
month_count = city_monthly.groupby("city")["month"].count().reset_index()
month_count.columns = ["city","months_with_data"]
seasonality = pd.merge(seasonality, month_count, on="city")
seasonality = seasonality[seasonality["months_with_data"] >= 8]

seasonality = seasonality.sort_values("seasonality_index", ascending=False).reset_index(drop=True)

print("Top 15 Most Seasonal Airports:")
print(seasonality[["city","seasonality_index","peak_month","total_pax"]
                  ].head(15).to_string(index=False))

print("\nTop 15 Most Stable Airports (year-round traffic):")
print(seasonality[["city","seasonality_index","peak_month","total_pax"]
                  ].tail(15).sort_values("seasonality_index").to_string(index=False))

print("\n-- Section 3: Route Peak Month Analysis -------------------------------")

route_monthly = pd.read_sql_query("""
    SELECT route, month, SUM(total_pax) AS pax
    FROM citypair
    WHERE year IN (2023, 2024)
    GROUP BY route, month
""", con)

route_season = route_monthly.groupby("route")["pax"].agg(
    max_pax="max", min_pax="min", avg_pax="mean", annual_pax="sum"
).reset_index()
route_season["seasonality_index"] = (
    (route_season["max_pax"] - route_season["min_pax"]) / route_season["avg_pax"] * 100
).round(1)

peak_route = route_monthly.loc[route_monthly.groupby("route")["pax"].idxmax()][["route","month"]]
peak_route.columns = ["route","peak_month"]
route_season = pd.merge(route_season, peak_route, on="route")

route_season = route_season[route_season["annual_pax"] > 50000]
route_season = route_season.sort_values("seasonality_index", ascending=False).reset_index(drop=True)

print("\nTop 15 Most Seasonal Routes (high traffic, strong seasonal swing):")
print(route_season[["route","seasonality_index","peak_month","annual_pax"]
                   ].head(15).to_string(index=False))

print("\nTop 15 Most Stable High-Traffic Routes:")
stable = route_season[route_season["annual_pax"] > 200000].tail(15).sort_values("seasonality_index")
print(stable[["route","seasonality_index","peak_month","annual_pax"]].to_string(index=False))

national_monthly.drop(columns=["month_num"]).to_csv(OUT1, index=False)
seasonality.to_csv(OUT2, index=False)
route_season.to_csv(OUT3, index=False)

print(f"\nSaved:")
print(f"   {OUT1}")
print(f"   {OUT2}")
print(f"   {OUT3}")

con.close()
