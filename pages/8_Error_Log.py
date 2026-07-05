from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.config import SKILLS
from src.data_utils import append_row, read_table, save_table
from src.ui import dataframe_download, setup_page

setup_page("Error Log")

st.title("🛠️ Error Log")
st.caption("Convert repeated mistakes into clear correction actions.")

with st.form("error_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        err_date = st.date_input("Date", value=date.today())
        skill = st.selectbox("Skill", SKILLS)
    with col2:
        status = st.selectbox("Status", ["Open", "Improving", "Fixed"])
        practice_id = st.text_input("Practice ID", placeholder="Optional")
    with col3:
        st.write("Mistake examples")
        st.caption("TFNG confusion, weak overview, short speaking answer, missed plural noun")
    mistake = st.text_input("Mistake", placeholder="What went wrong?")
    cause = st.text_area("Cause", placeholder="Why did it happen?", height=100)
    fix = st.text_area("Fix strategy", placeholder="What will you do next time?", height=100)
    submitted = st.form_submit_button("Add mistake", type="primary")

if submitted:
    if not mistake:
        st.error("Please add the mistake before saving.")
    else:
        append_row("error_log", {
            "Date": err_date.isoformat(),
            "Skill": skill,
            "Mistake": mistake,
            "Cause": cause,
            "Fix Strategy": fix,
            "Status": status,
            "Practice ID": practice_id,
        })
        st.success("Mistake added to Error Log.")

errors = read_table("error_log")
st.subheader("Error records")
if errors.empty:
    st.info("No error records yet.")
    st.stop()

edited = st.data_editor(
    errors,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_config={
        "Skill": st.column_config.SelectboxColumn("Skill", options=SKILLS),
        "Status": st.column_config.SelectboxColumn("Status", options=["Open", "Improving", "Fixed"]),
        "Cause": st.column_config.TextColumn("Cause", width="large"),
        "Fix Strategy": st.column_config.TextColumn("Fix Strategy", width="large"),
    },
    key="error_log_editor",
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Save error log changes", type="primary", use_container_width=True):
        save_table("error_log", edited)
        st.success("Error log saved.")
with col2:
    dataframe_download(errors, "error_log.csv")

st.subheader("Mistake summary")
summary = errors.groupby(["Skill", "Status"], as_index=False).size()
st.dataframe(summary, use_container_width=True, hide_index=True)
