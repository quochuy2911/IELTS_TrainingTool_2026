from __future__ import annotations

import streamlit as st

from src.data_utils import read_table, save_table
from src.ui import dataframe_download, setup_page

setup_page("Resources")

st.title("🔗 Resources")
st.caption("Official IELTS links, books, practice materials, and your personal notes.")

resources = read_table("resources")

st.write("Edit the table directly to add your own materials.")
edited = st.data_editor(
    resources,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_config={
        "Category": st.column_config.TextColumn("Category", width="small"),
        "Name": st.column_config.TextColumn("Name", width="medium"),
        "URL/Reference": st.column_config.TextColumn("URL/Reference", width="large"),
        "Use Case": st.column_config.TextColumn("Use Case", width="large"),
        "Notes": st.column_config.TextColumn("Notes", width="large"),
    },
    key="resources_editor",
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Save resources", type="primary", use_container_width=True):
        save_table("resources", edited)
        st.success("Resources saved.")
with col2:
    dataframe_download(resources, "resources.csv")

st.subheader("How to use resources")
st.write(
    "Use official IELTS materials for format, sample tasks, and band descriptors. "
    "Use Cambridge IELTS Academic tests for mock-test practice. "
    "Use general reading/listening sources only as supplements."
)
