from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data_utils import read_table, save_table
from src.drive_utils import render_attachment
from src.ui import dataframe_download, setup_page

setup_page("Speaking Review")

st.title("🎙️ Speaking Review")
st.caption("Review your speaking recordings, scripts, pronunciation notes, and self-ratings over time.")

archive = read_table("practice_archive")
files = read_table("file_metadata")

speaking = archive[archive["Skill"] == "Speaking"] if not archive.empty else archive
audio_files = files[(files["Skill"] == "Speaking") & (files["File Type"] == "audio")] if not files.empty else files

col1, col2, col3 = st.columns(3)
col1.metric("Speaking entries", len(speaking))
col2.metric("Audio recordings", len(audio_files))
if not speaking.empty:
    bands = pd.to_numeric(speaking["Estimated Band"].replace("", pd.NA), errors="coerce")
    col3.metric("Average speaking band", f"{bands.mean():.1f}" if bands.notna().any() else "N/A")
else:
    col3.metric("Average speaking band", "N/A")

if speaking.empty:
    st.info("No speaking practice saved yet. Add a Speaking entry in Practice Workspace and upload your recording.")
    st.stop()

c1, c2, c3 = st.columns(3)
with c1:
    part_filter = st.text_input("Filter by part/type", placeholder="Part 1, Part 2, Part 3")
with c2:
    search = st.text_input("Search topic/script", placeholder="keyword")
with c3:
    only_audio = st.checkbox("Only entries with audio", value=False)

view = speaking.copy()
if part_filter:
    view = view[view["Task Type"].str.contains(part_filter, case=False, na=False)]
if search:
    mask = view.apply(lambda row: search.lower() in " ".join(row.astype(str)).lower(), axis=1)
    view = view[mask]
if only_audio:
    audio_pids = set(audio_files["Practice ID"].tolist())
    view = view[view["Practice ID"].isin(audio_pids)]

st.subheader("Speaking practice list")
show_cols = ["Date", "Practice ID", "Task Type", "Title", "Estimated Band", "Main Problem", "Reflection", "Attachment Count"]
st.dataframe(view[show_cols], use_container_width=True, hide_index=True)

dataframe_download(view, "speaking_practice.csv", label="Download speaking records")

st.subheader("Review one recording / script")
ids = view["Practice ID"].tolist()
if not ids:
    st.info("No entries match the current filters.")
    st.stop()

selected = st.selectbox("Choose Speaking Practice ID", ids)
row = view[view["Practice ID"] == selected].iloc[0]
st.markdown(f"### {row['Title'] or row['Task Type']}")
meta1, meta2, meta3 = st.columns(3)
meta1.metric("Task type", row["Task Type"])
meta2.metric("Estimated band", row["Estimated Band"] or "N/A")
meta3.metric("Duration", f"{row['Duration Min']} min" if row["Duration Min"] else "N/A")

with st.expander("Question / prompt", expanded=True):
    st.write(row["Prompt"] or "No prompt saved.")
with st.expander("Script / transcript / notes", expanded=True):
    st.write(row["Answer"] or "No script/transcript saved.")
with st.expander("Self-review", expanded=False):
    st.write("**Main problem:**", row["Main Problem"] or "N/A")
    st.write("**Feedback:**", row["Feedback"] or "N/A")
    st.write("**Reflection:**", row["Reflection"] or "N/A")

entry_files = files[files["Practice ID"] == selected] if not files.empty else files
entry_audio = entry_files[entry_files["File Type"] == "audio"] if not entry_files.empty else entry_files
entry_other = entry_files[entry_files["File Type"] != "audio"] if not entry_files.empty else entry_files

st.subheader("Audio recordings")
if entry_audio.empty:
    st.info("No audio recording attached to this speaking practice.")
else:
    for _, frow in entry_audio.iterrows():
        render_attachment(frow, expanded=True)

if not entry_other.empty:
    st.subheader("Other attachments")
    for _, frow in entry_other.iterrows():
        render_attachment(frow)

st.subheader("Edit speaking feedback")
with st.form("speaking_feedback_form"):
    new_band = st.text_input("Estimated band", value=row["Estimated Band"])
    new_problem = st.text_input("Main problem", value=row["Main Problem"])
    new_feedback = st.text_area("Feedback / pronunciation notes", value=row["Feedback"], height=130)
    new_reflection = st.text_area("Reflection / next action", value=row["Reflection"], height=120)
    save = st.form_submit_button("Save speaking feedback", type="primary")

if save:
    full = archive.copy()
    idx = full.index[full["Practice ID"] == selected]
    if len(idx):
        i = idx[0]
        full.loc[i, "Estimated Band"] = new_band
        full.loc[i, "Main Problem"] = new_problem
        full.loc[i, "Feedback"] = new_feedback
        full.loc[i, "Reflection"] = new_reflection
        save_table("practice_archive", full)
        st.success("Speaking feedback saved.")
