from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import SKILLS
from src.data_utils import read_table, save_table
from src.drive_utils import render_attachment
from src.ui import dataframe_download, setup_page

setup_page("Practice Archive")

st.title("🗂️ Practice Archive")
st.caption("Review saved essays, reports, speaking scripts, reading/listening notes, and uploaded attachments.")

archive = read_table("practice_archive")
files = read_table("file_metadata")

if archive.empty:
    st.info("No saved practice yet. Add your first record in Practice Workspace.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    skill_filter = st.multiselect("Filter by skill", options=SKILLS, default=[])
with col2:
    task_filter = st.text_input("Filter by task type", placeholder="e.g., Task 2, Part 2, TFNG")
with col3:
    search = st.text_input("Search title/prompt/answer", placeholder="keyword")
with col4:
    only_with_files = st.checkbox("Only entries with files", value=False)

view = archive.copy()
if skill_filter:
    view = view[view["Skill"].isin(skill_filter)]
if task_filter:
    view = view[view["Task Type"].str.contains(task_filter, case=False, na=False)]
if search:
    mask = view.apply(lambda row: search.lower() in " ".join(row.astype(str)).lower(), axis=1)
    view = view[mask]
if only_with_files:
    view = view[pd.to_numeric(view["Attachment Count"], errors="coerce").fillna(0) > 0]

st.subheader("Saved practice table")
st.write("You can edit records here, including feedback and reflections. Click **Save archive changes** after editing.")
edited = st.data_editor(
    view,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_config={
        "Prompt": st.column_config.TextColumn("Prompt", width="large"),
        "Answer": st.column_config.TextColumn("Answer", width="large"),
        "Feedback": st.column_config.TextColumn("Feedback", width="large"),
        "Reflection": st.column_config.TextColumn("Reflection", width="large"),
    },
    key="practice_archive_editor",
)

col_save, col_download = st.columns(2)
with col_save:
    if st.button("Save archive changes", type="primary", use_container_width=True):
        full = archive.copy()
        edited_indexed = edited.set_index("Practice ID")
        full_indexed = full.set_index("Practice ID")
        for pid in edited_indexed.index:
            full_indexed.loc[pid, edited_indexed.columns] = edited_indexed.loc[pid]
        save_table("practice_archive", full_indexed.reset_index())
        st.success("Practice archive saved.")
with col_download:
    dataframe_download(archive, "practice_archive.csv")

st.subheader("Read one practice entry")
ids = view["Practice ID"].tolist()
if ids:
    selected = st.selectbox("Choose Practice ID", ids)
    row = view[view["Practice ID"] == selected].iloc[0]
    st.markdown(f"### {row['Title'] or selected}")
    meta1, meta2, meta3, meta4 = st.columns(4)
    meta1.metric("Skill", row["Skill"])
    meta2.metric("Task", row["Task Type"])
    meta3.metric("Band", row["Estimated Band"] or "N/A")
    meta4.metric("Attachments", row.get("Attachment Count", "0") or "0")
    with st.expander("Prompt / Question", expanded=True):
        st.write(row["Prompt"] or "No prompt saved.")
    with st.expander("Your answer", expanded=True):
        st.write(row["Answer"] or "No answer saved.")
    with st.expander("Feedback and reflection", expanded=False):
        st.write("**Main problem:**", row["Main Problem"] or "N/A")
        st.write("**Feedback:**", row["Feedback"] or "N/A")
        st.write("**Reflection:**", row["Reflection"] or "N/A")

    entry_files = files[files["Practice ID"] == selected] if not files.empty else files
    st.subheader("Attachments")
    if entry_files.empty:
        st.info("No attachments saved for this practice entry.")
    else:
        for _, frow in entry_files.iterrows():
            render_attachment(frow)
