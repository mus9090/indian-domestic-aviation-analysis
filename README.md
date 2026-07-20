# Indian Domestic Aviation — Route Performance & Growth Analysis (2019–2025)

An end-to-end data analytics project on India's domestic aviation network, built during a Data Analytics internship at the **Airports Authority of India (AAI)**. It consolidates seven years of DGCA monthly city-pair traffic data into a clean analytical database and surfaces the insights through four analytical pillars and an interactive Power BI dashboard.

## Problem

Despite the monthly aviation traffic data published by DGCA, there is no consolidated analytical view of how India's domestic route network has performed over the last five years. This makes it hard to see which airports are underserved, which routes recovered after COVID, and where airline competition is limited. This project closes that gap by consolidating DGCA data from 2019–2025 into a structured database and surfacing the findings clearly.

## Key Findings

| Pillar | Finding |
|---|---|
| **1 — COVID Recovery** | Domestic traffic reached **116% of 2019 levels by 2025**. Of 920 routes analysed, **478 are new since 2019** and 50 were permanently lost. Fastest recovery: Delhi–Nasik (+1198%). |
| **2 — Underserved Airports** | Across 128 airport-cities scored on passengers per lakh of population, **Ludhiana is the most underserved** — ~16 lakh people but only 39 passengers per lakh. |
| **3 — Seasonal Patterns** | **December is the single busiest month every year without exception** since 2019. Most seasonal: Goa and Leh–Srinagar (tourism); most stable: Delhi–Pune (business corridor). |
| **4 — Airline Competition (HHI)** | Of 594 routes in the Summer 2026 schedule, **zero are competitive** by HHI standards — **68% (405 routes) are outright monopolies**, and IndiGo alone operates ~60% of all scheduled flights. |

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

An interactive 4-page Power BI dashboard covering the four pillars — **National Overview · Route Performance · Underserved Airports · Airline Competition**. Open `Dashboard/Final_Dashboard.pbix` in Power BI Desktop to explore it.

## Author

**Muskaan Bhatia** — B.Tech CSE, MSIT Delhi. Data Analytics Intern, Airports Authority of India.
