"""
Uber Ride Bookings 2024 — Interactive Dashboard
Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Uber Ride Bookings 2024", page_icon="🚗", layout="wide")

RAW_FILE = "ncr_ride_bookings.csv"
CLEANED_FILE = "cleaned_uber_data.csv"

STATUS_COLORS = {
    "Completed": "#2E86AB",
    "Cancelled by Driver": "#E63946",
    "Cancelled by Customer": "#F26419",
    "No Driver Found": "#8E44AD",
    "Incomplete": "#F1C40F",
}


@st.cache_data
def load_and_clean_data():
    """Loads the cleaned CSV if it exists (produced by the notebook);
    otherwise cleans the raw file from scratch using the same logic
    as the analysis notebook, so this dashboard works standalone."""
    import os
    if os.path.exists(CLEANED_FILE):
        df = pd.read_csv(CLEANED_FILE, parse_dates=["Date", "Booking DateTime"])
        df["Booking Status"] = df["Booking Status"].astype("category")
        df["Vehicle Type"] = df["Vehicle Type"].astype("category")
        return df

    df = pd.read_csv(RAW_FILE, na_values=["null", "NULL", "Null", ""])

    df["Booking ID"] = df["Booking ID"].str.strip('"')
    df["Customer ID"] = df["Customer ID"].str.strip('"')
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].str.strip()

    df["Booking DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%Y-%m-%d %H:%M:%S")
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    df["Hour"] = df["Booking DateTime"].dt.hour
    df["Day of Week"] = df["Booking DateTime"].dt.day_name()
    df["Month"] = df["Booking DateTime"].dt.month_name()
    df["Month Num"] = df["Booking DateTime"].dt.month

    for c in ["Cancelled Rides by Customer", "Cancelled Rides by Driver", "Incomplete Rides"]:
        df[c] = df[c].fillna(0).astype(int)
    for c in ["Reason for cancelling by Customer", "Driver Cancellation Reason", "Incomplete Rides Reason"]:
        df[c] = df[c].fillna("Not Applicable")

    df.insert(0, "Row ID", range(1, len(df) + 1))
    return df


df = load_and_clean_data()

# ---------------------------------------------------------------- SIDEBAR
st.sidebar.title("Filters")
date_range = st.sidebar.date_input(
    "Date range",
    value=(df["Date"].min().date(), df["Date"].max().date()),
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date(),
)
vehicle_options = st.sidebar.multiselect(
    "Vehicle type", options=sorted(df["Vehicle Type"].unique()), default=list(sorted(df["Vehicle Type"].unique()))
)
status_options = st.sidebar.multiselect(
    "Booking status", options=sorted(df["Booking Status"].unique()), default=list(sorted(df["Booking Status"].unique()))
)

mask = (
    (df["Date"].dt.date >= date_range[0])
    & (df["Date"].dt.date <= date_range[-1])
    & (df["Vehicle Type"].isin(vehicle_options))
    & (df["Booking Status"].isin(status_options))
)
fdf = df[mask]
completed = fdf[fdf["Booking Status"] == "Completed"]

# ---------------------------------------------------------------- HEADER
st.title("🚗 Uber Ride Bookings 2024 — Dashboard")
st.caption("NCR ride-booking data — cleaning notes and full analysis are in the companion notebook.")

# ---------------------------------------------------------------- KPI ROW
k1, k2, k3, k4, k5 = st.columns(5)
total = len(fdf)
completion_rate = len(fdf[fdf["Booking Status"] == "Completed"]) / total * 100 if total else 0
cancel_rate = (fdf["Cancelled Rides by Customer"].sum() + fdf["Cancelled Rides by Driver"].sum()) / total * 100 if total else 0

k1.metric("Total Bookings", f"{total:,}")
k2.metric("Completion Rate", f"{completion_rate:.1f}%")
k3.metric("Cancellation Rate", f"{cancel_rate:.1f}%")
k4.metric("Total Revenue", f"{completed['Booking Value'].sum():,.0f}")
k5.metric("Avg Rating", f"{completed['Driver Ratings'].mean():.2f}" if len(completed) else "—")

st.divider()

# ---------------------------------------------------------------- ROW 1
c1, c2 = st.columns(2)
with c1:
    st.subheader("Booking Status")
    status_counts = fdf["Booking Status"].value_counts().reset_index()
    status_counts.columns = ["Booking Status", "Count"]
    fig = px.pie(status_counts, names="Booking Status", values="Count",
                 color="Booking Status", color_discrete_map=STATUS_COLORS, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Bookings by Vehicle Type")
    vt_counts = fdf["Vehicle Type"].value_counts().reset_index()
    vt_counts.columns = ["Vehicle Type", "Count"]
    fig = px.bar(vt_counts, x="Count", y="Vehicle Type", orientation="h", color="Count",
                 color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- ROW 2
c3, c4 = st.columns(2)
with c3:
    st.subheader("Bookings by Hour of Day")
    hourly = fdf.groupby("Hour").size().reset_index(name="Bookings")
    fig = px.area(hourly, x="Hour", y="Bookings")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Revenue by Vehicle Type")
    rev = completed.groupby("Vehicle Type", observed=True)["Booking Value"].sum().reset_index()
    fig = px.bar(rev.sort_values("Booking Value"), x="Booking Value", y="Vehicle Type", orientation="h",
                 color="Booking Value", color_continuous_scale="Oranges")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- ROW 3
st.subheader("Cancellation Reasons")
c5, c6 = st.columns(2)
with c5:
    cr = fdf.loc[fdf["Cancelled Rides by Customer"] == 1, "Reason for cancelling by Customer"].value_counts().reset_index()
    cr.columns = ["Reason", "Count"]
    fig = px.bar(cr, x="Count", y="Reason", orientation="h", title="By Customer",
                 color_discrete_sequence=["#F26419"])
    st.plotly_chart(fig, use_container_width=True)
with c6:
    dr = fdf.loc[fdf["Cancelled Rides by Driver"] == 1, "Driver Cancellation Reason"].value_counts().reset_index()
    dr.columns = ["Reason", "Count"]
    fig = px.bar(dr, x="Count", y="Reason", orientation="h", title="By Driver",
                 color_discrete_sequence=["#E63946"])
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- ROW 4
st.subheader("Fare vs. Distance")
if len(completed) > 0:
    sample = completed.sample(min(3000, len(completed)), random_state=42)
    fig = px.scatter(sample, x="Ride Distance", y="Booking Value", opacity=0.4,
                      color_discrete_sequence=["#2E86AB"], trendline="ols")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("View filtered data"):
    st.dataframe(fdf, use_container_width=True)
