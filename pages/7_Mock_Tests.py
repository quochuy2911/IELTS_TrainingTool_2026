from __future__ import annotations

from datetime import date

import streamlit as st

from src.config import TARGET_MIN_SKILL, TARGET_OVERALL
from src.data_utils import append_row, read_table, save_table
from src.scoring import readiness_label, round_ielts_overall
from src.ui import dataframe_download, setup_page

setup_page("Mock Tests")

st.title("🧪 Mock Test Tracker")
st.caption("Record full or partial IELTS Academic mock results and check target readiness.")

with st.form("mock_form"):
    col1, col2 = st.columns(2)
    with col1:
        mock_date = st.date_input("Date", value=date.today())
        source = st.text_input("Source", placeholder="e.g., Cambridge IELTS 18 Test 1")
    with col2:
        notes = st.text_area("Notes", height=100, placeholder="Timing issues, weak question types, test conditions...")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        listening = st.number_input("Listening", min_value=0.0, max_value=9.0, value=0.0, step=0.5)
    with c2:
        reading = st.number_input("Reading", min_value=0.0, max_value=9.0, value=0.0, step=0.5)
    with c3:
        writing = st.number_input("Writing", min_value=0.0, max_value=9.0, value=0.0, step=0.5)
    with c4:
        speaking = st.number_input("Speaking", min_value=0.0, max_value=9.0, value=0.0, step=0.5)

    submitted = st.form_submit_button("Add mock result", type="primary")

if submitted:
    scores = [listening, reading, writing, speaking]
    overall = round_ielts_overall(scores)
    readiness = readiness_label(listening, reading, writing, speaking, TARGET_OVERALL, TARGET_MIN_SKILL)
    append_row("mock_tests", {
        "Date": mock_date.isoformat(),
        "Source": source,
        "Listening": f"{listening:.1f}",
        "Reading": f"{reading:.1f}",
        "Writing": f"{writing:.1f}",
        "Speaking": f"{speaking:.1f}",
        "Overall": f"{overall:.1f}",
        "Readiness": readiness,
        "Notes": notes,
    })
    st.success(f"Mock saved. Overall: {overall:.1f} | Status: {readiness}")

mocks = read_table("mock_tests")

st.subheader("Mock records")
if mocks.empty:
    st.info("No mock test records yet.")
    st.stop()

edited = st.data_editor(mocks, use_container_width=True, hide_index=True, num_rows="dynamic", key="mock_editor")
col1, col2 = st.columns(2)
with col1:
    if st.button("Save mock table changes", type="primary", use_container_width=True):
        # Recalculate overall/readiness after manual edits.
        recalculated = edited.copy()
        for idx, row in recalculated.iterrows():
            try:
                scores = [float(row[s]) for s in ["Listening", "Reading", "Writing", "Speaking"]]
                recalculated.loc[idx, "Overall"] = f"{round_ielts_overall(scores):.1f}"
                recalculated.loc[idx, "Readiness"] = readiness_label(*scores, TARGET_OVERALL, TARGET_MIN_SKILL)
            except Exception:
                pass
        save_table("mock_tests", recalculated)
        st.success("Mock table saved and recalculated.")
with col2:
    dataframe_download(mocks, "mock_tests.csv")

st.subheader("Target rule")
st.write(f"Target: **Overall {TARGET_OVERALL}**, with **no skill below {TARGET_MIN_SKILL}**.")
