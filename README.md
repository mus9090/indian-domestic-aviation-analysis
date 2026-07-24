# Indian Domestic Aviation - Route Performance & Growth Analysis (2019–2025)

An end-to-end data analytics project on India's domestic aviation network, built during a Data Analytics internship at the **Airports Authority of India (AAI)**. It consolidates seven years of DGCA monthly city-pair traffic data into a clean analytical database and surfaces the insights through four analytical pillars and an interactive Power BI dashboard.

## Problem Statement

The DGCA publishes India's domestic air-traffic data every month, but it arrives as **60+ fragmented Excel files and operator-wise schedule PDFs** — never as a single, analysable picture. As a result, basic strategic questions about the national network have no ready answer: nobody can easily see how traffic recovered after COVID, which routes appeared or disappeared, which cities are starved of connectivity, or how competitive the market actually is.

This project closes that gap. It consolidates **seven years of DGCA city-pair traffic data (2019–2025)** plus the **Summer-2026 airline schedule** into one clean analytical database, and answers four concrete questions:

1. **Recovery & seasonality** — Has domestic air travel recovered to pre-COVID levels, and how does demand move through the year?
2. **Route performance** — Which routes came back after COVID, which were lost for good, and which are growing fastest?
3. **Connectivity gaps** — Which cities are most underserved relative to their population, and where are they concentrated?
4. **Market competition** — How competitive is the domestic network, or is it dominated by a handful of carriers?

The findings are delivered through four analytical pillars and an interactive four-page Power BI dashboard.

## Key Insights

At a glance, then in detail below:

| Pillar | Headline |
|---|---|
| **1 · Recovery & Seasonality** | Domestic traffic hit **116% of 2019 levels** by 2025; December is the peak month in 5 of 7 years. |
| **2 · Route Performance** | **478 new routes** since 2019 — but **50 lost for good**. |
| **3 · Underserved Airports** | **Ludhiana** — 16 lakh people, just **39 passengers per lakh** — is India's most underserved city. |
| **4 · Airline Competition** | **Zero** of 594 routes are competitive; **68% are monopolies** and IndiGo flies ~60% of all flights. |

### 1 · Recovery & Seasonality — *National Overview*
- Domestic passenger traffic reached **116% of 2019 volumes by 2025** — fully recovered and 16% above pre-pandemic levels.
- **December is the single busiest month in 5 of the 7 years**, driven by the year-end holiday surge. The exceptions are 2020 (COVID lockdown) and 2025, when November edged ahead of a December hit by widespread airline cancellations.
- Most seasonal markets: **Goa** and **Leh–Srinagar** (tourism-driven); most stable: **Delhi–Pune** (a steady business corridor).

### 2 · Route Performance — *COVID Recovery*
- Of **920 routes analysed**, **478 are new since 2019** and **50 were permanently lost** — the network expanded fast post-COVID, but a cluster of regional routes hit by airline exits never returned.
- Fastest recovery: **Delhi–Nasik (+1198%)**.
- Every route is scored on a recovery index (2025 vs 2019) and classified from *Fully Recovered & Grown* down to *Lost Route*.

### 3 · Underserved Airports
- **128 airport-cities** scored on passengers per lakh of population; **9 are critically underserved**.
- **Ludhiana is India's most underserved city** — ~16 lakh residents but only **39 air passengers per lakh** (just **631 total air passengers in all of 2025**), despite a population bigger than many state capitals.
- Underservice **concentrates in tier-2 cities of the northern plains and interior Maharashtra**. Most sit **150–300 km from the nearest major airport** — genuinely beyond easy reach of air travel, which argues they need their own connectivity, not just road links to a distant hub.

### 4 · Airline Competition — *HHI*
- Of **594 routes** in the Summer-2026 schedule, measured by the Herfindahl-Hirschman Index (HHI), **not one qualifies as competitive**.
- **68% (405 routes) are outright monopolies** and another 32% are highly concentrated — closer to a duopoly than an open market.
- **IndiGo alone operates ~60% (59.7%) of all scheduled domestic flights.** Even the busiest routes score near the HHI ceiling of 10,000 — the level at which a single carrier runs the entire route.

## Tech Stack

Python (Pandas), SQLite, Power BI, Jupyter, Excel/openpyxl, pdfplumber.

## Repository Structure

```
├── Scripts/                      # Data pipeline (run in order 01 → 07)
│   ├── 01_load_clean.py          # Clean 60+ raw DGCA Excel files → master_citypair.csv
│   ├── 02_load_sqlite.py         # Load master CSV → aviation.db (+ indexes)
│   ├── 03_covid_recovery.py      # Pillar 1
│   ├── 04_underserved_airports.py# Pillar 2
│   ├── 05_seasonal_analysis.py   # Pillar 3
│   ├── 06_hhi_competition.py     # Pillar 4 (parses airline schedule PDFs)
│   └── 07_powerbi_prep.py        # Sanitise CSVs + add map coordinates for Power BI
├── Notebooks/
│   └── project_verification.ipynb# Walkthrough / verification of all 4 pillars
├── Data/
│   ├── Cleaned/                  # Analysis output CSVs (one per pillar)
│   ├── powerbi/                  # Power BI-ready CSVs (sanitised + lat/long)
│   └── Lookup/
│       └── airport_city_population.csv
├── Database/
│   └── aviation.db               # SQLite database (table: citypair)
├── Dashboard/
│   └── Final_Dashboard.pbix      # Interactive 4-page Power BI dashboard
└── reports/                      # Charts / exported figures
```

## Data Pipeline

Run the scripts in order from the project root:

```bash
python Scripts/01_load_clean.py        # raw Excel → master_citypair.csv
python Scripts/02_load_sqlite.py       # → aviation.db
python Scripts/03_covid_recovery.py    # → covid_recovery.csv
python Scripts/04_underserved_airports.py
python Scripts/05_seasonal_analysis.py
python Scripts/06_hhi_competition.py   # → hhi_competition.csv, hhi_operator_shares.csv
python Scripts/07_powerbi_prep.py      # → Data/powerbi/*.csv
```

Scripts resolve paths relative to their own location, so they run from any clone location without editing.

## Data Sources

- **City-pair monthly traffic (2019–2025):** DGCA monthly domestic city-pair Excel files.
- **Airline flight schedule (Summer 2026):** DGCA approved domestic schedule, per operator (9 airlines).
- **Population:** Census 2011, city-level.

> **Note:** The bulky raw source files (DGCA monthly Excel files and the airline schedule PDFs) are **not committed** to keep the repo lean. The cleaned/analysed outputs they produce **are** included, so all results are viewable and the notebook + dashboard run as-is. To re-run `01`/`06` from scratch, download the raw DGCA files and place them in `Data/Raw/` and `Data/Lookup/flight_schedule/` respectively.

## Dashboard

An interactive 4-page Power BI dashboard covering the four pillars - **National Overview · Route Performance · Underserved Airports · Airline Competition**. Open `Dashboard/Final_Dashboard.pbix` in Power BI Desktop to explore it.

## Author

**Muskaan Bhatia** - B.Tech CSE, MSIT Delhi. Data Analytics Intern, Airports Authority of India.
