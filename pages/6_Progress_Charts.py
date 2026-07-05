from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_utils import read_table
from src.ui import band_to_float, setup_page

setup_page("Progress Charts")

st.title("📈 Progress Charts")
st.caption("Visualize study consistency, skill balance, practice bands, mock results, and repeated mistakes.")

study_log = read_table("study_log")
practice = read_table("practice_archive")
mock_tests = read_table("mock_tests")
errors = read_table("error_log")

# Study hours by week
st.subheader("Weekly study hours")
if study_log.empty:
    st.info("No study log records yet.")
else:
    tmp = study_log.copy()
    tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")
    tmp["Duration Min"] = pd.to_numeric(tmp["Duration Min"], errors="coerce").fillna(0)
    tmp = tmp.dropna(subset=["Date"])
    tmp["Week"] = tmp["Date"].dt.to_period("W").astype(str)
    weekly = tmp.groupby("Week", as_index=False)["Duration Min"].sum()
    weekly["Hours"] = weekly["Duration Min"] / 60
    fig = px.bar(weekly, x="Week", y="Hours", title="Total study hours per week")
    st.plotly_chart(fig, use_container_width=True)

# Skill distribution
st.subheader("Skill distribution")
if study_log.empty:
    st.info("No skill balance data yet.")
else:
    tmp = study_log.copy()
    tmp["Duration Min"] = pd.to_numeric(tmp["Duration Min"], errors="coerce").fillna(0)
    skill_dist = tmp.groupby("Skill", as_index=False)["Duration Min"].sum()
    skill_dist["Hours"] = skill_dist["Duration Min"] / 60
    fig = px.pie(skill_dist, names="Skill", values="Hours", title="Study time by IELTS skill")
    st.plotly_chart(fig, use_container_width=True)

# Practice band trend
st.subheader("Practice band trend")
if practice.empty:
    st.info("No practice band data yet.")
else:
    tmp = practice.copy()
    tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")
    tmp["Estimated Band"] = band_to_float(tmp["Estimated Band"])
    tmp = tmp.dropna(subset=["Date", "Estimated Band"])
    if tmp.empty:
        st.info("Practice records exist, but no estimated bands have been added yet.")
    else:
        fig = px.line(tmp.sort_values("Date"), x="Date", y="Estimated Band", color="Skill", markers=True,
                      title="Estimated band from saved practice")
        st.plotly_chart(fig, use_container_width=True)

# Mock score trend
st.subheader("Mock test score trend")
if mock_tests.empty:
    st.info("No mock test records yet.")
else:
    tmp = mock_tests.copy()
    tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")
    for col in ["Listening", "Reading", "Writing", "Speaking", "Overall"]:
        tmp[col] = pd.to_numeric(tmp[col], errors="coerce")
    long = tmp.melt(id_vars=["Date"], value_vars=["Listening", "Reading", "Writing", "Speaking", "Overall"],
                    var_name="Band Type", value_name="Band")
    long = long.dropna(subset=["Date", "Band"])
    if long.empty:
        st.info("Mock records exist, but scores are missing.")
    else:
        fig = px.line(long.sort_values("Date"), x="Date", y="Band", color="Band Type", markers=True,
                      title="IELTS mock band trend")
        st.plotly_chart(fig, use_container_width=True)

# Error patterns
st.subheader("Repeated mistake patterns")
if errors.empty:
    st.info("No error log records yet.")
else:
    err = errors.groupby("Skill", as_index=False).size()
    fig = px.bar(err, x="Skill", y="size", title="Number of logged mistakes by skill")
    st.plotly_chart(fig, use_container_width=True)
