from __future__ import annotations

from io import BytesIO
from pathlib import Path
import mimetypes
import re
from typing import Any

import streamlit as st

from .config import AUDIO_EXTENSIONS, IMAGE_EXTENSIONS
from .data_utils import (
    ROOT_DIR,
    UPLOAD_DIR,
    append_row,
    drive_configured,
    get_google_credentials,
    get_storage_settings,
    make_file_id,
)


def sanitize_filename(filename: str) -> str:
    name = Path(filename or "uploaded_file").name
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip()
    return name or "uploaded_file"


def file_type_from_name_and_mime(filename: str, mime_type: str | None) -> str:
    ext = Path(filename).suffix.lower().replace(".", "")
    mime = (mime_type or "").lower()
    if mime.startswith("image/") or ext in IMAGE_EXTENSIONS:
        return "image"
    if mime.startswith("audio/") or ext in AUDIO_EXTENSIONS:
        return "audio"
    if mime == "application/pdf" or ext == "pdf":
        return "pdf"
    return "document"


def _drive_service():
    try:
        from googleapiclient.discovery import build
    except Exception as exc:
        raise RuntimeError("google-api-python-client is not installed. Run: pip install -r requirements.txt") from exc
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = get_google_credentials(scopes)
    return build("drive", "v3", credentials=creds)


def upload_to_drive(uploaded_file, safe_name: str, practice_id: str) -> dict[str, str]:
    try:
        from googleapiclient.http import MediaIoBaseUpload
    except Exception as exc:
        raise RuntimeError("google-api-python-client is not installed. Run: pip install -r requirements.txt") from exc

    folder_id = get_storage_settings().get("google_drive_folder_id")
    if not folder_id:
        raise RuntimeError("Missing google_drive_folder_id in Streamlit secrets.")

    service = _drive_service()
    content = uploaded_file.getvalue()
    mime_type = uploaded_file.type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    body = {
        "name": f"{practice_id}_{safe_name}",
        "parents": [folder_id],
    }
    media = MediaIoBaseUpload(BytesIO(content), mimetype=mime_type, resumable=False)
    created = service.files().create(
        body=body,
        media_body=media,
        fields="id,name,webViewLink,webContentLink,mimeType,size",
        supportsAllDrives=True,
    ).execute()
    return {
        "drive_file_id": created.get("id", ""),
        "drive_url": created.get("webViewLink", ""),
        "mime_type": created.get("mimeType", mime_type),
        "size_bytes": str(created.get("size", len(content))),
    }


def save_local_upload(uploaded_file, safe_name: str, practice_id: str) -> dict[str, str]:
    folder = UPLOAD_DIR / practice_id
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / safe_name
    content = uploaded_file.getvalue()
    with target.open("wb") as f:
        f.write(content)
    return {
        "local_path": str(target.relative_to(ROOT_DIR)),
        "mime_type": uploaded_file.type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream",
        "size_bytes": str(len(content)),
    }


def save_uploaded_files(uploaded_files: list[Any], practice_id: str, date_str: str, skill: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for uploaded_file in uploaded_files or []:
        safe_name = sanitize_filename(uploaded_file.name)
        file_id = make_file_id()
        mime_type = uploaded_file.type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
        file_type = file_type_from_name_and_mime(safe_name, mime_type)

        provider = "local"
        local_path = ""
        drive_file_id = ""
        drive_url = ""
        size_bytes = str(len(uploaded_file.getvalue()))
        note = ""

        if drive_configured():
            try:
                drive_info = upload_to_drive(uploaded_file, safe_name, practice_id)
                provider = "google_drive"
                drive_file_id = drive_info.get("drive_file_id", "")
                drive_url = drive_info.get("drive_url", "")
                mime_type = drive_info.get("mime_type", mime_type)
                size_bytes = drive_info.get("size_bytes", size_bytes)
            except Exception as exc:
                # Keep the app usable even if Google Drive is not configured correctly.
                local_info = save_local_upload(uploaded_file, safe_name, practice_id)
                local_path = local_info["local_path"]
                mime_type = local_info["mime_type"]
                size_bytes = local_info["size_bytes"]
                note = f"Drive upload failed; saved locally. Error: {exc}"
        else:
            local_info = save_local_upload(uploaded_file, safe_name, practice_id)
            local_path = local_info["local_path"]
            mime_type = local_info["mime_type"]
            size_bytes = local_info["size_bytes"]

        row = {
            "File ID": file_id,
            "Practice ID": practice_id,
            "Date": date_str,
            "Skill": skill,
            "File Name": safe_name,
            "File Type": file_type,
            "MIME Type": mime_type,
            "Size Bytes": size_bytes,
            "Storage Provider": provider,
            "Local Path": local_path,
            "Drive File ID": drive_file_id,
            "Drive URL": drive_url,
            "Notes": note,
        }
        append_row("file_metadata", row)
        records.append(row)
    return records


def download_drive_file(file_id: str) -> bytes:
    service = _drive_service()
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    try:
        from googleapiclient.http import MediaIoBaseDownload
    except Exception as exc:
        raise RuntimeError("google-api-python-client is not installed. Run: pip install -r requirements.txt") from exc
    buffer = BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue()


def read_attachment_bytes(file_row) -> bytes | None:
    provider = str(file_row.get("Storage Provider", ""))
    if provider == "google_drive" and file_row.get("Drive File ID"):
        try:
            return download_drive_file(str(file_row.get("Drive File ID")))
        except Exception as exc:
            st.warning(f"Could not preview Drive file: {exc}")
            return None
    local_path = str(file_row.get("Local Path", ""))
    if local_path:
        path = ROOT_DIR / local_path
        if path.exists():
            return path.read_bytes()
    return None


def render_attachment(file_row, expanded: bool = False) -> None:
    file_name = str(file_row.get("File Name", "Attachment"))
    file_type = str(file_row.get("File Type", "document"))
    drive_url = str(file_row.get("Drive URL", ""))
    with st.expander(f"{file_type.title()}: {file_name}", expanded=expanded):
        content = read_attachment_bytes(file_row)
        if file_type == "image" and content:
            st.image(content, caption=file_name, use_container_width=True)
        elif file_type == "audio" and content:
            st.audio(content)
        elif content:
            st.download_button("Download attachment", content, file_name=file_name, use_container_width=True)
        else:
            st.info("Preview is not available. Use the stored link/path below.")
        if drive_url:
            st.markdown(f"[Open in Google Drive]({drive_url})")
        local_path = str(file_row.get("Local Path", ""))
        if local_path:
            st.caption(f"Local path: {local_path}")
        notes = str(file_row.get("Notes", ""))
        if notes:
            st.warning(notes)
