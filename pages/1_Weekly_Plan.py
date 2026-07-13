from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import PHASES, STATUS_OPTIONS
from src.data_utils import read_table, save_table
from src.ui import dataframe_download, setup_page

DATE_COLUMNS = ["Date Start", "Date End"]


def prepare_editor_dates(df: pd.DataFrame) -> pd.DataFrame:
    editor_df = df.copy()
    for col in DATE_COLUMNS:
        editor_df[col] = pd.to_datetime(editor_df[col], errors="coerce").dt.date
    return editor_df


def normalize_editor_dates(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for col in DATE_COLUMNS:
        dates = pd.to_datetime(normalized[col], errors="coerce")
        normalized[col] = dates.dt.strftime("%Y-%m-%d").fillna("")
    return normalized


setup_page("Weekly Plan")

st.title("📅 Weekly Plan")
st.caption("26-week IELTS Academic roadmap. Use this page only for planning; daily work happens in Study & Practice.")

plan = read_table("weekly_plan")

col1, col2, col3 = st.columns(3)
with col1:
    phase_filter = st.multiselect("Filter by phase", options=PHASES, default=[])
with col2:
    status_filter = st.multiselect("Filter by status", options=STATUS_OPTIONS, default=[])
with col3:
    search = st.text_input("Search objective/session", placeholder="e.g., Task 2, TFNG, mock")

view = plan.copy()
if phase_filter:
    view = view[view["Phase"].isin(phase_filter)]
if status_filter:
    view = view[view["Status"].isin(status_filter)]
if search:
    mask = view.apply(lambda row: search.lower() in " ".join(row.astype(str)).lower(), axis=1)
    view = view[mask]

st.write("Edit dates, sessions, status, and notes directly in the table. Click **Save changes** after editing.")
edited = st.data_editor(
    prepare_editor_dates(view),
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "Date Start": st.column_config.DateColumn("Date Start", format="YYYY-MM-DD"),
        "Date End": st.column_config.DateColumn("Date End", format="YYYY-MM-DD"),
        "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS),
        "Notes": st.column_config.TextColumn("Notes", width="large"),
        "Objective": st.column_config.TextColumn("Objective", width="medium"),
        "Session 1": st.column_config.TextColumn("Session 1", width="medium"),
        "Session 2": st.column_config.TextColumn("Session 2", width="medium"),
        "Session 3": st.column_config.TextColumn("Session 3", width="medium"),
        "Session 4": st.column_config.TextColumn("Session 4", width="medium"),
        "Optional Session": st.column_config.TextColumn("Optional Session", width="medium"),
    },
    disabled=["Week", "Phase"],
    key="weekly_plan_editor",
)

save_col, download_col = st.columns([1, 1])
with save_col:
    if st.button("Save changes", type="primary", use_container_width=True):
        edited = normalize_editor_dates(edited)
        missing_dates = edited[DATE_COLUMNS].eq("").any(axis=1)
        invalid_order = (
            pd.to_datetime(edited["Date End"], errors="coerce")
            < pd.to_datetime(edited["Date Start"], errors="coerce")
        )
        invalid_order = invalid_order.fillna(False)
        if missing_dates.any():
            st.error("Each edited row needs both a start date and an end date before saving.")
            st.stop()
        if invalid_order.any():
            bad_weeks = ", ".join(edited.loc[invalid_order, "Week"].astype(str))
            st.error(f"Date End must be on or after Date Start. Check week(s): {bad_weeks}.")
            st.stop()

        full = plan.copy()
        edited_indexed = edited.set_index("Week")
        full_indexed = full.set_index("Week")
        for week in edited_indexed.index:
            full_indexed.loc[week, edited_indexed.columns] = edited_indexed.loc[week]
        save_table("weekly_plan", full_indexed.reset_index())
        st.success("Weekly plan saved.")
with download_col:
    dataframe_download(plan, "weekly_plan.csv")

st.subheader("Phase summary")
summary = plan.groupby(["Phase", "Status"], as_index=False).size()
st.dataframe(summary, use_container_width=True, hide_index=True)
