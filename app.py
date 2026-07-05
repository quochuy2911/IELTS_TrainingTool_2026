from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import PLAN_START
from src.data_utils import get_app_settings, read_table
from src.scoring import safe_float
from src.ui import band_to_float, setup_page, storage_status_box

setup_page("Home")

settings = get_app_settings()
target_overall = settings["target_overall"]
target_min_skill = settings["target_min_skill"]
weekly_sessions = settings["weekly_sessions"]
exam_date = settings["exam_date"]

today = date.today()
days_remaining = (exam_date - today).days

st.title("🎓 IELTS Academic Preparation Dashboard")
st.caption("Simple control center: plan your week, practice all skills, review progress, and keep your IELTS work in one place.")

plan = read_table("weekly_plan")
study_log = read_table("study_log")
mock_tests = read_table("mock_tests")
practice = read_table("practice_archive")
errors = read_table("error_log")
files = read_table("file_metadata")


def current_phase_from_plan(plan_df: pd.DataFrame, current_day: date) -> str:
    if plan_df.empty:
        return "Not available"
    tmp = plan_df.copy()
    tmp["Date Start"] = pd.to_datetime(tmp["Date Start"], errors="coerce").dt.date
    tmp["Date End"] = pd.to_datetime(tmp["Date End"], errors="coerce").dt.date
    match = tmp[(tmp["Date Start"] <= current_day) & (tmp["Date End"] >= current_day)]
    if not match.empty:
        row = match.iloc[0]
        return f"Week {row['Week']} — {row['Phase']}"
    if current_day < PLAN_START:
        return "Before Week 1 — prepare setup"
    return "Plan completed — final exam preparation"


week_start = today - timedelta(days=today.weekday())
week_end = week_start + timedelta(days=6)
completed_this_week = 0
hours_this_week = 0.0
if not study_log.empty:
    tmp = study_log.copy()
    tmp["Date_parsed"] = pd.to_datetime(tmp["Date"], errors="coerce").dt.date
    tmp["Duration Min_num"] = pd.to_numeric(tmp["Duration Min"], errors="coerce").fillna(0)
    this_week = tmp[(tmp["Date_parsed"] >= week_start) & (tmp["Date_parsed"] <= week_end)]
    completed_this_week = len(this_week)
    hours_this_week = this_week["Duration Min_num"].sum() / 60

latest_overall = "No mock yet"
latest_min_skill = "No mock yet"
weakest_skill = "No data yet"
if not mock_tests.empty:
    tmp = mock_tests.copy()
    tmp["Date_parsed"] = pd.to_datetime(tmp["Date"], errors="coerce")
    tmp = tmp.sort_values("Date_parsed")
    latest = tmp.iloc[-1]
    latest_overall = latest.get("Overall", "") or "N/A"
    skill_scores = {skill: safe_float(latest.get(skill, ""), None) for skill in ["Listening", "Reading", "Writing", "Speaking"]}
    valid = {k: v for k, v in skill_scores.items() if v is not None}
    if valid:
        weakest_skill = min(valid, key=valid.get)
        latest_min_skill = f"{min(valid.values()):.1f}"
elif not practice.empty:
    tmp = practice.copy()
    tmp["Band_num"] = band_to_float(tmp["Estimated Band"])
    skill_avg = tmp.dropna(subset=["Band_num"]).groupby("Skill")["Band_num"].mean()
    if not skill_avg.empty:
        weakest_skill = skill_avg.idxmin()

st.subheader("Current status")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Days remaining", days_remaining)
col2.metric("This week", f"{completed_this_week} / {weekly_sessions} sessions", f"{hours_this_week:.1f} hours")
col3.metric("Latest mock overall", latest_overall)
col4.metric("Weakest skill", weakest_skill)

st.info(f"Current phase: **{current_phase_from_plan(plan, today)}**")

if weakest_skill in ["Writing", "Speaking", "Reading", "Listening"]:
    st.write(f"Next suggested session: **{weakest_skill} practice or repair**, because it is currently your weakest recorded skill.")
else:
    st.write("Next suggested session: add one record in **Study & Practice** to start tracking your real baseline.")

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Weekly study time")
    if study_log.empty:
        st.info("No study sessions yet. Add practice or manual logs to see this chart.")
    else:
        tmp = study_log.copy()
        tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")
        tmp["Duration Min"] = pd.to_numeric(tmp["Duration Min"], errors="coerce").fillna(0)
        tmp = tmp.dropna(subset=["Date"])
        tmp["Week"] = tmp["Date"].dt.to_period("W").astype(str)
        weekly = tmp.groupby("Week", as_index=False)["Duration Min"].sum()
        weekly["Hours"] = weekly["Duration Min"] / 60
        fig = px.bar(weekly, x="Week", y="Hours", title="Study hours by week")
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Skill balance")
    if study_log.empty:
        st.info("No skill distribution yet.")
    else:
        tmp = study_log.copy()
        tmp["Duration Min"] = pd.to_numeric(tmp["Duration Min"], errors="coerce").fillna(0)
        skill_time = tmp.groupby("Skill", as_index=False)["Duration Min"].sum()
        skill_time["Hours"] = skill_time["Duration Min"] / 60
        fig = px.pie(skill_time, names="Skill", values="Hours", title="Time by skill")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Archive snapshot")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Saved practice", len(practice))
c2.metric("Uploaded files", len(files))
c3.metric("Speaking audios", len(files[files["File Type"] == "audio"]) if not files.empty else 0)
c4.metric("Logged mistakes", len(errors))

st.subheader("Recent practice")
if practice.empty:
    st.info("No saved practice yet. Go to Study & Practice to save your first answer or record.")
else:
    cols = ["Date", "Skill", "Task Type", "Title", "Estimated Band", "Attachment Count", "Main Problem"]
    preview = practice.tail(5).iloc[::-1][cols]
    st.dataframe(preview, use_container_width=True, hide_index=True)

st.subheader("Target check")
st.write(
    f"Your current target is **Overall {target_overall:.1f}**, with **no skill below {target_min_skill:.1f}**. "
    "You can change this in **Settings & Storage** without editing code."
)
storage_status_box()
