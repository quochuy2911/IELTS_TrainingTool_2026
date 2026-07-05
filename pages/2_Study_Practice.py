from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.config import ALLOWED_UPLOAD_EXTENSIONS, BAND_OPTIONS, SKILLS
from src.data_utils import (
    add_task_type,
    append_row,
    get_task_type_options,
    make_practice_id,
    read_table,
    save_table,
)
from src.drive_utils import render_attachment, save_uploaded_files
from src.ui import dataframe_download, setup_page

setup_page("Study & Practice")

st.title("✍️ Study & Practice")
st.caption("One workspace for all four IELTS skills: practice, upload media, review archives, log sessions, and track mistakes.")

tab_new, tab_archive, tab_audio, tab_log, tab_errors = st.tabs([
    "New practice",
    "Archive",
    "Speaking/audio review",
    "Study log",
    "Error log",
])

with tab_new:
    st.subheader("Start a new IELTS practice session")
    st.write("Choose a skill first. The task-type list will adapt to that skill, and you can add your own task type when needed.")

    selected_skill = st.selectbox("Skill for this session", SKILLS, index=2, key="new_practice_skill")

    with st.expander("Add a custom task type for this skill"):
        custom_task = st.text_input("New task type", placeholder="e.g., Task 2 - Two-part question, Reading - Matching endings")
        custom_notes = st.text_input("Notes for this task type", placeholder="Optional")
        if st.button("Add custom task type", use_container_width=True):
            if add_task_type(selected_skill, custom_task, custom_notes):
                st.success(f"Added custom task type: {custom_task}")
                st.rerun()
            else:
                st.warning("This task type is empty or already exists for the selected skill.")

    task_options = get_task_type_options(selected_skill)

    with st.form("practice_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            practice_date = st.date_input("Date", value=date.today())
        with col2:
            task_type = st.selectbox("Task type", task_options)
            duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=60, step=5)
        with col3:
            resource = st.text_input("Resource", placeholder="e.g., Cambridge IELTS 18 Test 2")
            estimated_band = st.selectbox("Estimated band", BAND_OPTIONS, index=0)

        title = st.text_input("Title / Topic", placeholder="e.g., Task 2 - Technology and education")
        prompt = st.text_area("Prompt / Question", height=150, placeholder="Paste or type the IELTS prompt here.")

        answer_label = {
            "Writing": "Your answer / essay / report",
            "Speaking": "Script / transcript / speaking notes",
            "Reading": "Answer notes / mistake analysis",
            "Listening": "Answer notes / transcript review",
        }.get(selected_skill, "Your answer / notes")
        answer = st.text_area(answer_label, height=320, placeholder="Write your work, notes, transcript, or correction analysis here.")

        uploaded_files = st.file_uploader(
            "Attach images, audio, PDFs, or notes",
            type=ALLOWED_UPLOAD_EXTENSIONS,
            accept_multiple_files=True,
            help="Use images for charts/question screenshots, and audio for speaking recordings.",
        )

        col4, col5 = st.columns(2)
        with col4:
            main_problem = st.text_input("Main problem", placeholder="e.g., weak overview, short examples, TFNG confusion")
            feedback = st.text_area("Feedback / correction notes", height=120)
        with col5:
            reflection = st.text_area("Reflection / next action", height=170, placeholder="What will you improve next time?")

        count_as_session = st.checkbox("Count this practice as one study session", value=True)
        add_to_error_log = st.checkbox("Also add the main problem to Error Log", value=False)

        submitted = st.form_submit_button("Save practice", type="primary")

    if uploaded_files:
        st.subheader("Attachment preview before saving")
        for f in uploaded_files:
            if f.type and f.type.startswith("image/"):
                st.image(f, caption=f.name, use_container_width=True)
            elif f.type and f.type.startswith("audio/"):
                st.audio(f)
            else:
                st.caption(f"Attached: {f.name} ({f.type or 'unknown type'})")

    if submitted:
        has_content = any([title.strip(), prompt.strip(), answer.strip(), uploaded_files])
        if not has_content:
            st.error("Please add at least a title, prompt, answer, or attachment before saving.")
        else:
            practice_id = make_practice_id()
            saved_files = save_uploaded_files(uploaded_files or [], practice_id, practice_date.isoformat(), selected_skill)
            attachment_count = len(saved_files)
            append_row("practice_archive", {
                "Practice ID": practice_id,
                "Date": practice_date.isoformat(),
                "Skill": selected_skill,
                "Task Type": task_type,
                "Title": title,
                "Prompt": prompt,
                "Answer": answer,
                "Resource": resource,
                "Duration Min": duration,
                "Estimated Band": estimated_band,
                "Main Problem": main_problem,
                "Feedback": feedback,
                "Reflection": reflection,
                "Attachment Count": attachment_count,
            })
            if count_as_session:
                append_row("study_log", {
                    "Date": practice_date.isoformat(),
                    "Skill": selected_skill,
                    "Task Type": task_type,
                    "Duration Min": duration,
                    "Resource": resource,
                    "Score/Accuracy": "",
                    "Estimated Band": estimated_band,
                    "Reflection": reflection,
                    "Practice ID": practice_id,
                })
            if add_to_error_log and main_problem:
                append_row("error_log", {
                    "Date": practice_date.isoformat(),
                    "Skill": selected_skill,
                    "Mistake": main_problem,
                    "Cause": "",
                    "Fix Strategy": reflection,
                    "Status": "Open",
                    "Practice ID": practice_id,
                })
            st.success(f"Practice saved. ID: {practice_id}")
            if attachment_count:
                st.success(f"Saved {attachment_count} attachment(s).")

with tab_archive:
    st.subheader("Practice archive")
    archive = read_table("practice_archive")
    files = read_table("file_metadata")

    if archive.empty:
        st.info("No saved practice yet. Add your first record in the New practice tab.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            skill_filter = st.multiselect("Filter by skill", options=SKILLS, default=[], key="archive_skill_filter")
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

        st.write("Edit archive fields directly, then save changes.")
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
            key="practice_archive_editor_merged",
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

        st.subheader("Review one practice entry")
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
            with st.expander("Your work / notes", expanded=True):
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
        else:
            st.info("No entries match the current filters.")

with tab_audio:
    st.subheader("Speaking and audio review")
    archive = read_table("practice_archive")
    files = read_table("file_metadata")
    speaking = archive[archive["Skill"] == "Speaking"] if not archive.empty else archive
    audio_files = files[files["File Type"] == "audio"] if not files.empty else files

    col1, col2, col3 = st.columns(3)
    col1.metric("Speaking entries", len(speaking))
    col2.metric("Audio recordings", len(audio_files))
    if not speaking.empty:
        bands = pd.to_numeric(speaking["Estimated Band"].replace("", pd.NA), errors="coerce")
        col3.metric("Average speaking band", f"{bands.mean():.1f}" if bands.notna().any() else "N/A")
    else:
        col3.metric("Average speaking band", "N/A")

    if speaking.empty:
        st.info("No speaking practice saved yet. Add a Speaking entry in the New practice tab and upload your recording.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            part_filter = st.text_input("Filter by part/type", placeholder="Part 1, Part 2, Part 3")
        with c2:
            search = st.text_input("Search topic/script", placeholder="keyword", key="speaking_search")
        with c3:
            only_audio = st.checkbox("Only entries with audio", value=True)

        view = speaking.copy()
        if part_filter:
            view = view[view["Task Type"].str.contains(part_filter, case=False, na=False)]
        if search:
            mask = view.apply(lambda row: search.lower() in " ".join(row.astype(str)).lower(), axis=1)
            view = view[mask]
        if only_audio and not audio_files.empty:
            audio_pids = set(audio_files["Practice ID"].tolist())
            view = view[view["Practice ID"].isin(audio_pids)]

        show_cols = ["Date", "Practice ID", "Task Type", "Title", "Estimated Band", "Main Problem", "Reflection", "Attachment Count"]
        st.dataframe(view[show_cols], use_container_width=True, hide_index=True)
        dataframe_download(view, "speaking_practice.csv", label="Download speaking records")

        ids = view["Practice ID"].tolist()
        if ids:
            selected = st.selectbox("Choose Speaking Practice ID", ids)
            row = view[view["Practice ID"] == selected].iloc[0]
            st.markdown(f"### {row['Title'] or row['Task Type']}")
            with st.expander("Question / prompt", expanded=True):
                st.write(row["Prompt"] or "No prompt saved.")
            with st.expander("Script / transcript / notes", expanded=True):
                st.write(row["Answer"] or "No script/transcript saved.")

            entry_files = files[files["Practice ID"] == selected] if not files.empty else files
            entry_audio = entry_files[entry_files["File Type"] == "audio"] if not entry_files.empty else entry_files
            st.subheader("Audio recordings")
            if entry_audio.empty:
                st.info("No audio recording attached to this speaking practice.")
            else:
                for _, frow in entry_audio.iterrows():
                    render_attachment(frow, expanded=True)

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
        else:
            st.info("No speaking entries match the current filters.")

with tab_log:
    st.subheader("Manual study log")
    selected_skill = st.selectbox("Skill", SKILLS, key="manual_log_skill")
    log_task_options = get_task_type_options(selected_skill)

    with st.expander("Add a custom task type for manual logging"):
        custom_task = st.text_input("New manual-log task type", key="manual_custom_task")
        if st.button("Add manual-log task type"):
            if add_task_type(selected_skill, custom_task):
                st.success(f"Added custom task type: {custom_task}")
                st.rerun()
            else:
                st.warning("This task type is empty or already exists.")

    with st.form("study_log_form_merged"):
        col1, col2, col3 = st.columns(3)
        with col1:
            log_date = st.date_input("Date", value=date.today(), key="manual_log_date")
        with col2:
            task_type = st.selectbox("Task type", log_task_options, key="manual_log_task")
            duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=60, step=5, key="manual_log_duration")
        with col3:
            resource = st.text_input("Resource", placeholder="e.g., Cambridge IELTS 18", key="manual_log_resource")
            band = st.selectbox("Estimated band", BAND_OPTIONS, index=0, key="manual_log_band")
        score = st.text_input("Score / Accuracy", placeholder="e.g., 32/40, 10/13, Band 6.5")
        reflection = st.text_area("Reflection", placeholder="What did you learn or need to fix?")
        submitted = st.form_submit_button("Add manual log", type="primary")

    if submitted:
        append_row("study_log", {
            "Date": log_date.isoformat(),
            "Skill": selected_skill,
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
    if log.empty:
        st.info("No study sessions logged yet.")
    else:
        edited = st.data_editor(log, use_container_width=True, hide_index=True, num_rows="dynamic", key="study_log_editor_merged")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save study log changes", type="primary", use_container_width=True):
                save_table("study_log", edited)
                st.success("Study log saved.")
        with col2:
            dataframe_download(log, "study_log.csv")

with tab_errors:
    st.subheader("Error log")
    selected_skill = st.selectbox("Skill", SKILLS, key="error_skill")
    with st.form("error_form_merged"):
        col1, col2, col3 = st.columns(3)
        with col1:
            err_date = st.date_input("Date", value=date.today(), key="error_date")
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
                "Skill": selected_skill,
                "Mistake": mistake,
                "Cause": cause,
                "Fix Strategy": fix,
                "Status": status,
                "Practice ID": practice_id,
            })
            st.success("Mistake added to Error Log.")

    errors = read_table("error_log")
    if errors.empty:
        st.info("No error records yet.")
    else:
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
            key="error_log_editor_merged",
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
