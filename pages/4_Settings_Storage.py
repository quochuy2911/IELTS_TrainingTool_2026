from __future__ import annotations

import streamlit as st

from src.config import BAND_OPTIONS, SKILLS
from src.data_utils import (
    get_app_settings,
    read_table,
    save_app_settings,
    save_table,
    storage_summary,
)
from src.ui import dataframe_download, setup_page, storage_status_box

setup_page("Settings & Storage")

st.title("⚙️ Settings & Storage")
st.caption("Edit your target setup, manage skill-specific task types, and check Google Sheets/Drive storage.")

tab_target, tab_tasks, tab_storage = st.tabs(["Target setup", "Task types", "Storage setup"])

with tab_target:
    st.subheader("Editable IELTS target")
    st.write("These values are saved in the app data, so you can change them without editing Python code.")
    settings = get_app_settings()
    with st.form("target_settings_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            target_overall = st.selectbox(
                "Target overall",
                [x for x in BAND_OPTIONS if x],
                index=[x for x in BAND_OPTIONS if x].index(f"{settings['target_overall']:.1f}") if f"{settings['target_overall']:.1f}" in [x for x in BAND_OPTIONS if x] else 15,
            )
        with c2:
            target_min_skill = st.selectbox(
                "Minimum skill band",
                [x for x in BAND_OPTIONS if x],
                index=[x for x in BAND_OPTIONS if x].index(f"{settings['target_min_skill']:.1f}") if f"{settings['target_min_skill']:.1f}" in [x for x in BAND_OPTIONS if x] else 13,
            )
        with c3:
            weekly_sessions = st.number_input("Target sessions/week", min_value=1, max_value=14, value=int(settings["weekly_sessions"]), step=1)
        with c4:
            exam_date = st.date_input("Expected exam date", value=settings["exam_date"])
        save = st.form_submit_button("Save target setup", type="primary")

    if save:
        save_app_settings(float(target_overall), float(target_min_skill), int(weekly_sessions), exam_date)
        st.success("Target setup saved. Reload or change pages to see the new sidebar values.")

    st.subheader("Raw settings table")
    settings_table = read_table("settings")
    st.dataframe(settings_table, use_container_width=True, hide_index=True)

with tab_tasks:
    st.subheader("Skill-specific task types")
    st.write("The Study & Practice page uses this table to adapt the task-type list based on the selected skill.")
    tasks = read_table("task_types")

    edited = st.data_editor(
        tasks,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Skill": st.column_config.SelectboxColumn("Skill", options=SKILLS),
            "Active": st.column_config.SelectboxColumn("Active", options=["Yes", "No"]),
            "Custom": st.column_config.SelectboxColumn("Custom", options=["Yes", "No"]),
            "Task Type": st.column_config.TextColumn("Task Type", width="large"),
            "Notes": st.column_config.TextColumn("Notes", width="large"),
        },
        key="task_types_editor",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save task types", type="primary", use_container_width=True):
            save_table("task_types", edited)
            st.success("Task types saved.")
    with col2:
        dataframe_download(tasks, "task_types.csv")

    st.info("Tip: set Active = No if you want to hide a task type without deleting it.")

with tab_storage:
    st.subheader("Google Sheets / Drive setup")
    storage_status_box()
    summary = storage_summary()

    st.write(f"**Google Sheet ID configured:** {'Yes' if summary['google_sheet_id'] else 'No'}")
    st.write(f"**Google Drive folder ID configured:** {'Yes' if summary['google_drive_folder_id'] else 'No'}")
    st.write(f"**Google Sheets ready:** {summary['cloud_ready']}")
    st.write(f"**Google Drive ready:** {summary['drive_ready']}")

    st.subheader("Connection test")
    if st.button("Test record storage", type="primary"):
        try:
            df = read_table("weekly_plan")
            st.success(f"Record storage works. Weekly plan rows loaded: {len(df)}")
        except Exception as exc:
            st.error(f"Record storage test failed: {exc}")

    st.subheader("Recommended deployment setup")
    st.markdown(
        """
1. Create a Google Cloud service account and enable Google Sheets API + Google Drive API.
2. Create one Google Sheet for dashboard records.
3. Create one Google Drive folder for uploaded images/audio.
4. Share both the Sheet and Drive folder with the service account email as Editor.
5. Add the service account JSON and IDs to Streamlit Community Cloud secrets.

Use the included `.streamlit/secrets.example.toml` file as the template. Do **not** commit your real `secrets.toml` to GitHub.
"""
    )

    st.subheader("Secrets template")
    st.code(
        """
[storage]
google_sheet_id = "paste_your_google_sheet_id_here"
google_drive_folder_id = "paste_your_google_drive_folder_id_here"

[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your_cert_url"
universe_domain = "googleapis.com"
""".strip(),
        language="toml",
    )
