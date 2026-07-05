from __future__ import annotations

from datetime import date

import streamlit as st

from src.config import ALLOWED_UPLOAD_EXTENSIONS, BAND_OPTIONS, SKILLS, TASK_TYPES
from src.data_utils import append_row, make_practice_id
from src.drive_utils import save_uploaded_files
from src.ui import setup_page

setup_page("Practice Workspace")

st.title("✍️ Practice Workspace")
st.caption("Write IELTS practice directly inside the app, attach images/audio, then save everything to your archive.")

st.info(
    "Recommended workflow: paste the IELTS prompt, write your answer or notes, upload any chart/question screenshot/audio recording, "
    "then save it. The entry can automatically count as a study session."
)

with st.form("practice_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        practice_date = st.date_input("Date", value=date.today())
        skill = st.selectbox("Skill", SKILLS, index=2)
    with col2:
        task_type = st.selectbox("Task type", TASK_TYPES[skill])
        duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=60, step=5)
    with col3:
        resource = st.text_input("Resource", placeholder="e.g., Cambridge IELTS 18 Test 2")
        estimated_band = st.selectbox("Estimated band", BAND_OPTIONS, index=0)

    title = st.text_input("Title / Topic", placeholder="e.g., Task 2 - Technology and education")
    prompt = st.text_area("Prompt / Question", height=150, placeholder="Paste or type the IELTS prompt here.")
    answer = st.text_area("Your answer / script / notes", height=320, placeholder="Write your essay, report, speaking script, transcript, or practice notes here.")

    uploaded_files = st.file_uploader(
        "Attach images, audio, PDFs, or notes",
        type=ALLOWED_UPLOAD_EXTENSIONS,
        accept_multiple_files=True,
        help="Use images for Writing Task 1 charts/question screenshots, and audio for Speaking recordings.",
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
        saved_files = save_uploaded_files(uploaded_files or [], practice_id, practice_date.isoformat(), skill)
        attachment_count = len(saved_files)
        append_row("practice_archive", {
            "Practice ID": practice_id,
            "Date": practice_date.isoformat(),
            "Skill": skill,
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
                "Skill": skill,
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
                "Skill": skill,
                "Mistake": main_problem,
                "Cause": "",
                "Fix Strategy": reflection,
                "Status": "Open",
                "Practice ID": practice_id,
            })
        st.success(f"Practice saved. ID: {practice_id}")
        if attachment_count:
            st.success(f"Saved {attachment_count} attachment(s).")
        st.info("Open Practice Archive or Speaking Review to review saved work and attachments.")

st.divider()
st.subheader("Recommended use by skill")
st.write(
    "**Writing:** upload the Task 1 chart screenshot or paste the Task 2 prompt, then write your full answer.\n\n"
    "**Speaking:** upload your recording, paste the cue card/question, then add a short self-review.\n\n"
    "**Reading/Listening:** save the passage/section source, score, mistake pattern, and correction notes."
)
