from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import PHASES, STATUS_OPTIONS
from src.data_utils import read_table, save_table
from src.ui import dataframe_download, setup_page

setup_page("Weekly Plan")

st.title("📅 Weekly Study Plan")
st.caption("26-week IELTS Academic roadmap from July 2026 to December 2026.")

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

st.write("Edit status and notes directly in the table. Click **Save changes** after editing.")
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS),
        "Notes": st.column_config.TextColumn("Notes", width="large"),
        "Objective": st.column_config.TextColumn("Objective", width="medium"),
        "Session 1": st.column_config.TextColumn("Session 1", width="medium"),
        "Session 2": st.column_config.TextColumn("Session 2", width="medium"),
        "Session 3": st.column_config.TextColumn("Session 3", width="medium"),
        "Session 4": st.column_config.TextColumn("Session 4", width="medium"),
        "Optional Session": st.column_config.TextColumn("Optional Session", width="medium"),
    },
    disabled=["Week", "Date Start", "Date End", "Phase"],
    key="weekly_plan_editor",
)

save_col, download_col = st.columns([1, 1])
with save_col:
    if st.button("Save changes", type="primary", use_container_width=True):
        # Merge edited filtered rows back into the full plan by Week number.
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
