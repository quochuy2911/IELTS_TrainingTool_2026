from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from .config import APP_TITLE, TARGET_MIN_SKILL, TARGET_OVERALL
from .data_utils import clear_google_cache, ensure_data_files, restore_backup, storage_summary, zip_data_bytes


def setup_page(title: str):
    st.set_page_config(page_title=f"{title} | {APP_TITLE}", page_icon="🎓", layout="wide")
    ensure_data_files()
    render_sidebar()


def render_sidebar():
    st.sidebar.title("🎓 IELTS Academic")
    st.sidebar.caption(f"Target: Overall {TARGET_OVERALL} | No skill below {TARGET_MIN_SKILL}")
    summary = storage_summary()
    st.sidebar.divider()
    st.sidebar.write("**Storage**")
    st.sidebar.caption(f"Records: {summary['records']}")
    st.sidebar.caption(f"Files: {summary['files']}")
    if summary["records"] == "Local CSV" or summary["files"] == "Local uploads folder":
        st.sidebar.info("For deployment, configure Google Sheets/Drive in Streamlit secrets.")
    st.sidebar.divider()

    if st.sidebar.button("Refresh Google data", use_container_width=True):
        clear_google_cache()
        st.sidebar.success("Google data cache cleared. Reload or change pages to fetch fresh data.")

    if st.sidebar.button("Prepare backup download", use_container_width=True):
        st.session_state["_backup_bytes"] = zip_data_bytes()

    if "_backup_bytes" in st.session_state:
        st.sidebar.download_button(
            "Download prepared backup",
            data=st.session_state["_backup_bytes"],
            file_name=f"ielts_dashboard_backup_{date.today().isoformat()}.zip",
            mime="application/zip",
            use_container_width=True,
        )

    uploaded = st.sidebar.file_uploader("Restore backup (.zip)", type=["zip"])
    if uploaded is not None:
        if st.sidebar.button("Restore backup now", use_container_width=True):
            restored = restore_backup(uploaded)
            if restored:
                st.sidebar.success(f"Restored {len(restored)} table(s). Refresh the page.")
            else:
                st.sidebar.warning("No valid dashboard CSV files were found in this backup.")
    st.sidebar.divider()
    st.sidebar.caption("Use the Storage Setup page before deploying for long-term use.")


def dataframe_download(df: pd.DataFrame, file_name: str, label: str = "Download CSV"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, data=csv, file_name=file_name, mime="text/csv")


def band_to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("", pd.NA), errors="coerce")


def display_empty_message(table_name: str):
    st.info(f"No {table_name} records yet. Add your first record from the form above.")


def storage_status_box():
    summary = storage_summary()
    col1, col2 = st.columns(2)
    col1.metric("Record storage", summary["records"])
    col2.metric("File storage", summary["files"])
    if summary["records"] == "Google Sheets" and summary["files"] == "Google Drive":
        st.success("Cloud storage is configured for both records and uploaded files.")
    else:
        st.warning("Cloud storage is not fully configured. Local fallback is active for at least one storage type.")
