# Mentor review demo - Indian domestic aviation project progress
# Data: DGCA 2019-2025

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from IPython.display import display, HTML

BASE    = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "database" / "aviation.db"
con     = sqlite3.connect(DB_PATH)

plt.rcParams.update({
    "figure.facecolor" : "#0f1117", "axes.facecolor"  : "#0f1117",
    "axes.edgecolor"   : "#333333", "axes.labelcolor" : "#cccccc",
    "axes.titlecolor"  : "#ffffff", "xtick.color"     : "#cccccc",
    "ytick.color"      : "#cccccc", "text.color"      : "#ffffff",
    "grid.color"       : "#222222", "grid.linestyle"  : "--",
    "font.family"      : "sans-serif", "font.size"    : 11,
})

display(HTML("""
<div style='background:#1a1a2e;padding:24px;border-radius:12px;
            border-left:5px solid #3498db;margin-bottom:16px'>
  <h1 style='color:#3498db;margin:0'>Indian Domestic Aviation</h1>
  <h2 style='color:#ffffff;margin:6px 0'>Route Performance & Growth Analysis</h2>
  <p style='color:#aaaaaa;margin:0'>
     AAI Internship Project &nbsp;|&nbsp; Muskaan, MSIT Delhi &nbsp;|&nbsp;
     Data: DGCA Monthly City Pair Traffic 2019–2025
  </p>
</div>
"""))

# Section 1 - Data pipeline
display(HTML("<h2 style='color:#3498db;border-bottom:1px solid #333;padding-bottom:6px'>"
             "Section 1 — Data Pipeline</h2>"))

total_rows   = pd.read_sql_query("SELECT COUNT(*) AS n FROM citypair", con)["n"][0]
total_routes = pd.read_sql_query("SELECT COUNT(DISTINCT route) AS n FROM citypair", con)["n"][0]
year_range   = pd.read_sql_query("SELECT MIN(year) AS y1, MAX(year) AS y2 FROM citypair", con)
nulls        = pd.read_sql_query("""
    SELECT SUM(CASE WHEN total_pax IS NULL THEN 1 ELSE 0 END) AS n FROM citypair
""", con)["n"][0]

display(HTML(f"""
<div style='display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px'>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #3498db;min-width:160px;text-align:center'>
    <div style='font-size:28px;font-weight:bold;color:#3498db'>{total_rows:,}</div>
    <div style='color:#aaa;font-size:13px'>Total Rows</div>
  </div>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #2ecc71;min-width:160px;text-align:center'>
    <div style='font-size:28px;font-weight:bold;color:#2ecc71'>{total_routes:,}</div>
    <div style='color:#aaa;font-size:13px'>Unique Routes</div>
  </div>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #f39c12;min-width:160px;text-align:center'>
    <div style='font-size:28px;font-weight:bold;color:#f39c12'>
        {year_range["y1"][0]}–{year_range["y2"][0]}</div>
    <div style='color:#aaa;font-size:13px'>Years Covered</div>
  </div>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #2ecc71;min-width:160px;text-align:center'>
    <div style='font-size:28px;font-weight:bold;color:#2ecc71'>{nulls}</div>
    <div style='color:#aaa;font-size:13px'>Null Values</div>
  </div>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #9b59b6;min-width:160px;text-align:center'>
    <div style='font-size:28px;font-weight:bold;color:#9b59b6'>60</div>
    <div style='color:#aaa;font-size:13px'>Raw DGCA Files Processed</div>
  </div>
</div>
"""))

display(HTML("<b style='color:#aaa'>Rows per Year:</b>"))
rows_per_year = pd.read_sql_query("""
    SELECT year, COUNT(*) AS rows, COUNT(DISTINCT route) AS unique_routes,
           ROUND(SUM(total_pax)/1e7,2) AS passengers_crore
    FROM citypair GROUP BY year ORDER BY year
""", con)
display(rows_per_year.style
    .set_properties(**{"background-color":"#0d2137","color":"white","border":"1px solid #222"})
    .set_table_styles([{"selector":"th","props":[("background","#1a1a2e"),
                                                  ("color","#3498db"),("padding","8px")]}])
    .hide(axis="index")
    .bar(subset=["passengers_crore"], color="#1a4a6e")
)

# Section 2 - COVID recovery analysis
display(HTML("<h2 style='color:#2ecc71;border-bottom:1px solid #333;padding-bottom:6px;margin-top:32px'>"
             "Section 2 — COVID Recovery Analysis</h2>"))

# National trend
national = pd.read_sql_query("""
    SELECT year, SUM(total_pax) AS total_passengers, COUNT(DISTINCT route) AS active_routes
    FROM citypair GROUP BY year ORDER BY year
""", con)
baseline = national.loc[national["year"]==2019,"total_passengers"].values[0]
national["recovery_pct"] = (national["total_passengers"]/baseline*100).round(1)
national["pax_crore"]    = (national["total_passengers"]/1e7).round(2)

# Route recovery
pax_2019 = pd.read_sql_query("""
    SELECT route, SUM(total_pax) AS pax_2019 FROM citypair
    WHERE year=2019 GROUP BY route HAVING SUM(total_pax)>=10000
""", con)
pax_2024 = pd.read_sql_query("""
    SELECT route, SUM(total_pax) AS pax_2024 FROM citypair
    WHERE year=2024 GROUP BY route
""", con)
recovery = pd.merge(pax_2019, pax_2024, on="route", how="outer")

def ridx(r):
    if pd.isna(r["pax_2019"]) or r["pax_2019"]==0: return None
    if pd.isna(r["pax_2024"]) or r["pax_2024"]==0: return 0
    return round(r["pax_2024"]/r["pax_2019"]*100,1)

def rlabel(r):
    if pd.isna(r["pax_2019"]) or r["pax_2019"]==0: return "New Route"
    if pd.isna(r["pax_2024"]) or r["pax_2024"]==0: return "Lost Route"
    i=r["recovery_index"]
    if i>=110: return "Fully Recovered & Grown"
    if i>=90:  return "Recovered"
    if i>=50:  return "Partially Recovered"
    return "Critically Lagging"

recovery["recovery_index"] = recovery.apply(ridx, axis=1)
recovery["status"]         = recovery.apply(rlabel, axis=1)
recovery["pax_2019"]       = recovery["pax_2019"].fillna(0).astype(int)
recovery["pax_2024"]       = recovery["pax_2024"].fillna(0).astype(int)
recovery["pax_change"]     = recovery["pax_2024"] - recovery["pax_2019"]

sc = recovery["status"].value_counts()

r2024 = national.loc[national["year"]==2024,"recovery_pct"].values[0]
r2025 = national.loc[national["year"]==2025,"recovery_pct"].values[0]

display(HTML(f"""
<div style='display:flex;gap:16px;flex-wrap:wrap;margin-bottom:20px'>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #2ecc71;min-width:180px;text-align:center'>
    <div style='font-size:32px;font-weight:bold;color:#2ecc71'>{r2024}%</div>
    <div style='color:#aaa;font-size:13px'>Recovery vs 2019 (2024)</div>
  </div>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #3498db;min-width:180px;text-align:center'>
    <div style='font-size:32px;font-weight:bold;color:#3498db'>{r2025}%</div>
    <div style='color:#aaa;font-size:13px'>Recovery vs 2019 (2025)</div>
  </div>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #2ecc71;min-width:180px;text-align:center'>
    <div style='font-size:32px;font-weight:bold;color:#2ecc71'>{sc.get("Fully Recovered & Grown",0)+sc.get("Recovered",0)}</div>
    <div style='color:#aaa;font-size:13px'>Routes Fully Recovered</div>
  </div>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #3498db;min-width:180px;text-align:center'>
    <div style='font-size:32px;font-weight:bold;color:#3498db'>{sc.get("New Route",0)}</div>
    <div style='color:#aaa;font-size:13px'>New Routes Since 2019</div>
  </div>
  <div style='background:#0d2137;padding:16px 24px;border-radius:10px;
              border-top:3px solid #e74c3c;min-width:180px;text-align:center'>
    <div style='font-size:32px;font-weight:bold;color:#e74c3c'>{sc.get("Lost Route",0)}</div>
    <div style='color:#aaa;font-size:13px'>Routes Permanently Lost</div>
  </div>
</div>
"""))

# Chart
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.patch.set_facecolor("#0f1117")

# Recovery curve
ax = axes[0]
colors_bar = ["#2ecc71" if r>=100 else "#e74c3c" if r<60 else "#f39c12"
              for r in national["recovery_pct"]]
bars = ax.bar(national["year"], national["pax_crore"], color=colors_bar, alpha=0.85, width=0.6, zorder=3)
ax.axhline(y=national["pax_crore"].iloc[0], color="#2ecc71", linestyle="--", linewidth=1, alpha=0.5)
ax.set_title("Passengers by Year (Crore)", fontweight="bold")
ax.set_ylabel("Passengers (Crore)")
ax.grid(axis="y", zorder=0)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0fCr"))
for bar, r, p in zip(bars, national["recovery_pct"], national["pax_crore"]):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
            f"{r}%", ha="center", fontsize=8,
            color="#2ecc71" if r>=100 else "#f39c12")

# Donut
ax = axes[1]
status_order = ["Fully Recovered & Grown","Recovered","Partially Recovered",
                "Critically Lagging","Lost Route","New Route"]
cmap = {"Fully Recovered & Grown":"#2ecc71","Recovered":"#82e0aa",
        "Partially Recovered":"#f39c12","Critically Lagging":"#e74c3c",
        "Lost Route":"#922b21","New Route":"#3498db"}
sizes  = [sc.get(s,0) for s in status_order]
colors = [cmap[s] for s in status_order]
ax.pie(sizes, colors=colors,
       autopct=lambda p: f"{p:.0f}%" if p>4 else "",
       pctdistance=0.75, startangle=140,
       wedgeprops=dict(width=0.5, edgecolor="#0f1117", linewidth=1.5))
ax.set_title("Route Recovery Distribution", fontweight="bold")
patches = [mpatches.Patch(color=cmap[s], label=f"{s} ({sc.get(s,0)})")
           for s in status_order]
ax.legend(handles=patches, loc="lower center", bbox_to_anchor=(0.5,-0.3),
          fontsize=7, ncol=2, framealpha=0.1)

# Top lagging
ax = axes[2]
lag = recovery[(recovery["status"]=="Critically Lagging")&
               (recovery["pax_2019"]>50000)].nsmallest(8,"recovery_index").sort_values("recovery_index")
ax.barh(lag["route"], lag["recovery_index"], color="#e74c3c", alpha=0.85, height=0.6)
ax.set_title("Most Lagging Routes\n(Had >50K pax in 2019)", fontweight="bold")
ax.set_xlabel("Recovery Index (%)")
ax.grid(axis="x", zorder=0)
for i,(_,row) in enumerate(lag.iterrows()):
    ax.text(row["recovery_index"]+0.5, i, f"{row['recovery_index']:.1f}%", va="center", fontsize=8)

plt.tight_layout()
plt.savefig(BASE / "reports" / "mentor_demo_chart.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.show()

# Top routes table
display(HTML("<b style='color:#aaa'>Top 10 Fastest Growing Routes:</b>"))
top10 = recovery[recovery["status"]=="Fully Recovered & Grown"].nlargest(10,"recovery_index")[
    ["route","pax_2019","pax_2024","recovery_index","status"]]
display(top10.style
    .set_properties(**{"background-color":"#0d2137","color":"white","border":"1px solid #222"})
    .set_table_styles([{"selector":"th","props":[("background","#1a1a2e"),("color","#2ecc71"),("padding","8px")]}])
    .hide(axis="index")
    .bar(subset=["recovery_index"], color="#1a4a1a")
)

# Section 3 - what's next
display(HTML("""
<h2 style='color:#f39c12;border-bottom:1px solid #333;padding-bottom:6px;margin-top:32px'>
Section 3 — Work in Progress</h2>
<div style='display:flex;gap:16px;flex-wrap:wrap'>
  <div style='background:#0d2137;padding:16px;border-radius:10px;
              border-left:4px solid #2ecc71;flex:1;min-width:200px'>
    <div style='color:#2ecc71;font-weight:bold'>Pillar 1 — COVID Recovery</div>
    <div style='color:#aaa;font-size:13px;margin-top:6px'>Complete. 980 routes analysed.</div>
  </div>
  <div style='background:#0d2137;padding:16px;border-radius:10px;
              border-left:4px solid #f39c12;flex:1;min-width:200px'>
    <div style='color:#f39c12;font-weight:bold'>Pillar 2 — Underserved Airports</div>
    <div style='color:#aaa;font-size:13px;margin-top:6px'>
        Script ready. Pax per lakh population metric. Running next.</div>
  </div>
  <div style='background:#0d2137;padding:16px;border-radius:10px;
              border-left:4px solid #e74c3c;flex:1;min-width:200px'>
    <div style='color:#e74c3c;font-weight:bold'>Pillar 3 — UDAN / Seasonal</div>
    <div style='color:#aaa;font-size:13px;margin-top:6px'>
        Awaiting mentor direction on UDAN vs seasonal analysis.</div>
  </div>
  <div style='background:#0d2137;padding:16px;border-radius:10px;
              border-left:4px solid #9b59b6;flex:1;min-width:200px'>
    <div style='color:#9b59b6;font-weight:bold'>Pillar 4 — Airline Efficiency</div>
    <div style='color:#aaa;font-size:13px;margin-top:6px'>
        Load factor PDFs identified. Parser script next.</div>
  </div>
</div>
<br>
<div style='background:#0d2137;padding:16px;border-radius:10px;border-left:4px solid #3498db'>
  <div style='color:#3498db;font-weight:bold'>Final Deliverable</div>
  <div style='color:#aaa;font-size:13px;margin-top:6px'>
      4-page interactive Power BI dashboard connecting all four pillars.
      Target: fully built after all analysis scripts are complete.
  </div>
</div>
"""))

con.close()
print("\nDemo complete.")
