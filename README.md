# Uber Ride Bookings 2024 — Analysis & Dashboard

A cleaning + analysis + dashboard project on 150,000 Uber ride bookings from the NCR (Delhi-NCR) region, 2024.

## What's in this folder

| File | What it is |
|---|---|
| `KavitaBijarniya_UberRideAnalysis.ipynb` | **The main file.** Loads the raw data, cleans it, analyzes it, visualizes it, and generates the dashboard script — all in one notebook. |
| `README.md` | This file. |
| `requirements.txt` | Python packages needed to run everything. |
| `KavitaBijarniya_ProjectReport.docx` | Plain-language write-up of what the data actually shows, plus a full column-by-column data dictionary. |
| `ncr_ride_bookings.csv` | The raw dataset (keep this here — you provide it). |
| `app.py` | *Generated* — created when you run the notebook's dashboard cell. Not included until you run it. |
| `cleaned_uber_data.csv` | *Generated* — the cleaned dataset, saved by the notebook. |

<img width="1789" height="250" alt="image" src="https://github.com/user-attachments/assets/e030d12f-4163-450a-a05e-9c3774690b40" />

 ## Project Overview
 
This project takes a raw, messy ride-booking export and turns it into a clean dataset, a full exploratory analysis, and an interactive dashboard. It covers the full pipeline a data analyst is actually asked to do: figuring out *why* data is missing before deciding what to do about it, finding real patterns vs. noise, and packaging the result so someone non-technical could open a dashboard and explore it themselves.
 
One of the more interesting findings: fare, distance, and trip time turn out to be **uncorrelated** with each other in this dataset — the opposite of what you'd expect from a real ride-hailing system. That's called out directly in the analysis rather than glossed over (see `DATA_INSIGHTS.md`).
 
<img width="1367" height="490" alt="image" src="https://github.com/user-attachments/assets/df7db4c2-d1cb-4c48-aec3-86921a027560" />

**Skills demonstrated:** data cleaning (missing-value logic, not blind imputation), exploratory data analysis, data visualization (Matplotlib/Seaborn/Plotly), Python/Pandas, Streamlit dashboard development.

## How to run it

**1. Install the requirements**
```bash
pip install -r requirements.txt
```

**2. Make sure the raw data is in this folder**

Place `ncr_ride_bookings.csv` in the same folder as the notebook.

**3. Run the notebook**

Open `Uber_Ride_Analysis.ipynb` in Jupyter (`jupyter notebook` or VS Code) and run all cells, top to bottom. This will:
- Clean the raw data
- Print and chart the full analysis
- Save `cleaned_uber_data.csv`
- Generate `app.py` (the dashboard) — this is the one cell that uses `%%writefile`, since Streamlit apps can't run inside a notebook

**4. Launch the dashboard**

Once the notebook has run at least once (so `app.py` exists), open a terminal in this folder and run:
```bash
streamlit run app.py
```
This opens an interactive, filterable dashboard in your browser. Note: `app.py` also works even if you skip the notebook — it cleans the raw CSV itself if `cleaned_uber_data.csv` isn't present yet.

## Why the dashboard is a separate file if "everything is in one notebook"

It is — the dashboard's entire source code lives inside the notebook, in one cell. But Streamlit apps have to be run as their own script (`streamlit run ...`), they can't execute inside a Jupyter cell. So that one cell's job is to *write out* `app.py` using Jupyter's `%%writefile` magic. Nothing about the dashboard was written anywhere except inside the notebook.

## A note on how the missing data was handled

This dataset has a lot of blank cells, but most of them aren't errors — they're blanks that make sense once you know the ride's outcome (a cancelled ride, for example, never has a fare, because no trip happened). The notebook explains this in detail in Section 3–4, but the short version:

- Flags and "reason" columns: filled in where a blank clearly means "not applicable"
- Fare, distance, time, and rating columns: left blank where the underlying event never happened — **not** filled with averages or zeros, since that would invent data that was never real

See `KavitaBijarniya_ProjectReport.docx` for the reasoning behind each decision.
