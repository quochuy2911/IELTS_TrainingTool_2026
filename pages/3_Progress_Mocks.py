from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import SKILLS
from src.data_utils import append_row, get_app_settings, read_table, save_table
from src.scoring import readiness_label, round_ielts_overall
from src.ui import dataframe_download, setup_page

setup_page("Progress & Mocks")

settings = get_app_settings()
target_overall = settings["target_overall"]
target_min_skill = settings["target_min_skill"]

st.title("📈 Progress & Mock Tests")
st.caption("Track study consistency, skill balance, practice bands, mock-test results, and readiness for your target.")

tab_progress, tab_mocks = st.tabs(["Progress charts", "Mock tests"])

with tab_progress:
    study_log = read_table("study_log")
    practice = read_table("practice_archive")
    mock_tests = read_table("mock_tests")
    errors = read_table("error_log")

    st.subheader("Study consistency")
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
        fig = px.bar(weekly, x="Week", y="Hours", title="Weekly study hours")
        st.plotly_chart(fig, use_container_width=True)

        skill_time = tmp.groupby("Skill", as_index=False)["Duration Min"].sum()
        skill_time["Hours"] = skill_time["Duration Min"] / 60
        fig = px.bar(skill_time, x="Skill", y="Hours", title="Study hours by skill")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Practice band trend")
    if practice.empty:
        st.info("No practice records with estimated bands yet.")
    else:
        tmp = practice.copy()
        tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")
        tmp["Estimated Band"] = pd.to_numeric(tmp["Estimated Band"], errors="coerce")
        tmp = tmp.dropna(subset=["Date", "Estimated Band"])
        if tmp.empty:
            st.info("Practice records exist, but estimated bands are missing.")
        else:
            fig = px.line(tmp.sort_values("Date"), x="Date", y="Estimated Band", color="Skill", markers=True,
                          title="Estimated practice band over time")
            st.plotly_chart(fig, use_container_width=True)

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
            fig.add_hline(y=target_overall, line_dash="dash", annotation_text=f"Overall target {target_overall:.1f}")
            fig.add_hline(y=target_min_skill, line_dash="dot", annotation_text=f"Minimum skill {target_min_skill:.1f}")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Repeated mistake patterns")
    if errors.empty:
        st.info("No error log records yet.")
    else:
        err = errors.groupby(["Skill", "Status"], as_index=False).size()
        fig = px.bar(err, x="Skill", y="size", color="Status", title="Logged mistakes by skill and status")
        st.plotly_chart(fig, use_container_width=True)

with tab_mocks:
    st.subheader("Add mock test result")
    st.caption(f"Current target: Overall {target_overall:.1f}, no skill below {target_min_skill:.1f}. Change this in Settings & Storage.")
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
        readiness = readiness_label(listening, reading, writing, speaking, target_overall, target_min_skill)
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
    else:
        edited = st.data_editor(mocks, use_container_width=True, hide_index=True, num_rows="dynamic", key="mock_editor")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save mock table changes", type="primary", use_container_width=True):
                recalculated = edited.copy()
                for idx, row in recalculated.iterrows():
                    try:
                        scores = [float(row[s]) for s in ["Listening", "Reading", "Writing", "Speaking"]]
                        recalculated.loc[idx, "Overall"] = f"{round_ielts_overall(scores):.1f}"
                        recalculated.loc[idx, "Readiness"] = readiness_label(*scores, target_overall, target_min_skill)
                    except Exception:
                        pass
                save_table("mock_tests", recalculated)
                st.success("Mock table saved and recalculated.")
        with col2:
            dataframe_download(mocks, "mock_tests.csv")
