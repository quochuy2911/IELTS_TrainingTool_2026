from __future__ import annotations

import streamlit as st

from src.data_utils import cloud_configured, drive_configured, read_table, storage_summary
from src.ui import setup_page, storage_status_box

setup_page("Storage Setup")

st.title("☁️ Storage Setup")
st.caption("Use this page to check whether Google Sheets and Google Drive are ready before deployment.")

storage_status_box()
summary = storage_summary()

st.subheader("Current configuration")
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
2. Create one Google Sheet for the IELTS dashboard records.
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

st.subheader("Storage behavior")
st.write(
    "If Google Sheets is configured correctly, all records are stored in your Google Sheet. "
    "If Google Drive is configured correctly, uploaded images and audio are stored in your Drive folder. "
    "If either service is not configured, the app falls back to local CSV files and a local uploads folder so you can still test the app."
)
