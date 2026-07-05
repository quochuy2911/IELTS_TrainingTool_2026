from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.config import BAND_OPTIONS, SKILLS, TASK_TYPES
from src.data_utils import append_row, read_table, save_table
from src.ui import dataframe_download, setup_page

setup_page("Study Log")

st.title("📘 Study Log")
st.caption("Manual session tracker. Practice Workspace can also auto-create records here.")

with st.form("study_log_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        log_date = st.date_input("Date", value=date.today())
        skill = st.selectbox("Skill", SKILLS)
    with col2:
        task_type = st.selectbox("Task type", TASK_TYPES[skill])
        duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=60, step=5)
    with col3:
        resource = st.text_input("Resource", placeholder="e.g., Cambridge IELTS 18")
        band = st.selectbox("Estimated band", BAND_OPTIONS, index=0)
    score = st.text_input("Score / Accuracy", placeholder="e.g., 32/40, 10/13, Band 6.5")
    reflection = st.text_area("Reflection", placeholder="What did you learn? What will you fix next time?", height=120)
    submitted = st.form_submit_button("Add study session", type="primary")

if submitted:
    append_row("study_log", {
        "Date": log_date.isoformat(),
        "Skill": skill,
        "Task Type": task_type,
        "Duration Min": duration,
        "Resource": resource,
        "Score/Accuracy": score,
        "Estimated Band": band,
        "Reflection": reflection,
        "Practice ID": "",
    })
    st.success("Study session added.")

log = read_table("study_log")

st.subheader("Session records")
if log.empty:
    st.info("No study sessions yet.")
    st.stop()

edited = st.data_editor(
    log,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_config={
        "Skill": st.column_config.SelectboxColumn("Skill", options=SKILLS),
        "Reflection": st.column_config.TextColumn("Reflection", width="large"),
    },
    key="study_log_editor",
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Save study log changes", type="primary", use_container_width=True):
        save_table("study_log", edited)
        st.success("Study log saved.")
with col2:
    dataframe_download(log, "study_log.csv")

st.subheader("Summary")
tmp = log.copy()
tmp["Duration Min"] = pd.to_numeric(tmp["Duration Min"], errors="coerce").fillna(0)
summary = tmp.groupby("Skill", as_index=False)["Duration Min"].sum()
summary["Hours"] = (summary["Duration Min"] / 60).round(2)
st.dataframe(summary[["Skill", "Hours"]], use_container_width=True, hide_index=True)
