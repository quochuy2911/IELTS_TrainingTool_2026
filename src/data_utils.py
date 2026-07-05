from __future__ import annotations

from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Any
import zipfile

import pandas as pd

from .config import DEFAULT_EXAM_DATE, DEFAULT_TARGET_MIN_SKILL, DEFAULT_TARGET_OVERALL, DEFAULT_TASK_TYPES, DEFAULT_WEEKLY_SESSIONS, SKILLS

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

TABLE_SCHEMAS: dict[str, list[str]] = {
    "weekly_plan": [
        "Week", "Date Start", "Date End", "Phase", "Objective", "Session 1", "Session 2",
        "Session 3", "Session 4", "Optional Session", "Status", "Notes"
    ],
    "study_log": [
        "Date", "Skill", "Task Type", "Duration Min", "Resource", "Score/Accuracy",
        "Estimated Band", "Reflection", "Practice ID"
    ],
    "mock_tests": [
        "Date", "Source", "Listening", "Reading", "Writing", "Speaking", "Overall", "Readiness", "Notes"
    ],
    "error_log": [
        "Date", "Skill", "Mistake", "Cause", "Fix Strategy", "Status", "Practice ID"
    ],
    "practice_archive": [
        "Practice ID", "Date", "Skill", "Task Type", "Title", "Prompt", "Answer", "Resource",
        "Duration Min", "Estimated Band", "Main Problem", "Feedback", "Reflection", "Attachment Count"
    ],
    "file_metadata": [
        "File ID", "Practice ID", "Date", "Skill", "File Name", "File Type", "MIME Type", "Size Bytes",
        "Storage Provider", "Local Path", "Drive File ID", "Drive URL", "Notes"
    ],
    "settings": ["Setting", "Value", "Description"],
    "task_types": ["Skill", "Task Type", "Active", "Custom", "Notes"],
    "resources": ["Category", "Name", "URL/Reference", "Use Case", "Notes"],
}


def table_path(table_name: str) -> Path:
    return DATA_DIR / f"{table_name}.csv"


def build_weekly_plan() -> pd.DataFrame:
    rows = []
    start = date(2026, 7, 6)
    week_specs = [
        (1, "Foundation + Diagnostic", "Baseline and format familiarisation", "Timed Academic Reading diagnostic", "Timed Listening diagnostic", "Write Task 2 baseline essay", "Record Speaking Part 2 answer", "Task 1 baseline report"),
        (2, "Foundation + Diagnostic", "Reading fundamentals and error review", "Skimming/scanning + one passage", "TFNG/YNNG drills", "Vocabulary from passage", "Speaking Part 1 expansion", "Review Week 1 errors"),
        (3, "Foundation + Diagnostic", "Listening fundamentals", "Listening Sections 1-2", "Transcript review", "Spelling/numbers/plurals drill", "Task 1 overview paragraph", "Weakest skill repair"),
        (4, "Foundation + Diagnostic", "Writing structure setup", "Task 1 line/bar chart", "Task 2 structure practice", "Full Task 2 essay", "Speaking Part 2 recording", "Rewrite one weak paragraph"),
        (5, "Skill Building", "Matching headings and Task 1 charts", "Reading matching headings", "Listening Sections 1-2", "Task 1 line/bar chart", "Speaking Part 1 fluency", "Task 2 mini-plan"),
        (6, "Skill Building", "TFNG and opinion essays", "Reading TFNG/YNNG", "Listening Section 3", "Task 2 opinion essay", "Speaking Part 2 structure", "Transcript review"),
        (7, "Skill Building", "Completion questions and tables", "Reading sentence completion", "Listening Section 4 notes", "Task 1 table", "Speaking Part 3 reasons", "Vocabulary notebook"),
        (8, "Skill Building", "Multiple choice and maps", "Reading multiple choice", "Listening map/diagram", "Task 2 discussion essay", "Speaking technology topic", "Error log update"),
        (9, "Skill Building", "Full Reading/Listening pressure", "Full Academic Reading test", "Full Listening test", "Task 1 process/map", "Speaking 2-minute cue card", "Review wrong answers"),
        (10, "Skill Building", "Repair week", "Reading error repair", "Listening error repair", "Rewrite old essays", "Speaking self-correction", "Mock score review"),
        (11, "Band 7 Development", "Task 2 argument quality", "Task 2 thesis + topic sentences", "Task 2 full essay", "Reading passage timing", "Speaking Part 3 development", "Rewrite essay"),
        (12, "Band 7 Development", "Academic Reading speed", "Full Reading test", "TFNG/headings repair", "Listening Section 3", "Task 1 mixed chart", "Vocabulary review"),
        (13, "Band 7 Development", "Listening accuracy", "Listening Sections 3-4", "Transcript shadowing", "Reading passage", "Speaking fluency", "Task 2 examples"),
        (14, "Band 7 Development", "Task 1 overview mastery", "Task 1 line/bar", "Task 1 table/pie", "Task 1 map/process", "Speaking Part 2", "Task 2 conclusion cleanup"),
        (15, "Band 7 Development", "Speaking expansion", "Speaking Part 1", "Speaking Part 2", "Speaking Part 3", "Reading full test", "Task 2 advantages/disadvantages"),
        (16, "Band 7 Development", "Half mock and review", "Timed Listening", "Timed Reading", "Task 2 in 40 min", "Speaking full mock", "Error repair"),
        (17, "Mock Practice + Weakness Repair", "Full LR mock", "Full Listening test", "Full Reading test", "Wrong-answer analysis", "Task 1 report", "Weakest skill repair"),
        (18, "Mock Practice + Weakness Repair", "Full Writing mock", "Task 1 in 20 min", "Task 2 in 40 min", "Self-assessment with band descriptors", "Speaking Part 3", "Rewrite weak answer"),
        (19, "Mock Practice + Weakness Repair", "Speaking mock week", "Full Speaking mock 1", "Full Speaking mock 2", "Vocabulary repair", "Listening Section 4", "Reflection update"),
        (20, "Mock Practice + Weakness Repair", "Full LRW stamina", "Full Listening", "Full Reading", "Full Writing", "Mock test review", "Rest/repair session"),
        (21, "Mock Practice + Weakness Repair", "Lowest skill repair", "Weakest skill session 1", "Weakest skill session 2", "Weakest skill session 3", "Speaking light practice", "Progress chart review"),
        (22, "Mock Practice + Weakness Repair", "Full mock and comparison", "Full Listening", "Full Reading", "Task 1 + Task 2", "Speaking mock", "Compare to Week 1"),
        (23, "Final Preparation", "Test simulation", "Full LRW mock", "Full Speaking mock", "Mock review", "Task 1 quick review", "Error log review"),
        (24, "Final Preparation", "Writing polishing", "Task 1 visual types review", "Task 2 essay types review", "Reusable idea bank", "Speaking Part 3", "Rewrite old essay"),
        (25, "Final Preparation", "Accuracy week", "Listening common traps", "Reading TFNG/headings", "Writing grammar cleanup", "Speaking fluency", "No new strategy"),
        (26, "Final Preparation", "Light final review", "Review templates", "Review vocabulary notebook", "Light Listening/Reading", "Speaking confidence practice", "Plan exam-week routine"),
    ]
    for week, phase, objective, s1, s2, s3, s4, optional in week_specs:
        week_start = start + timedelta(days=(week - 1) * 7)
        week_end = week_start + timedelta(days=6)
        if week == 26:
            week_end = date(2026, 12, 31)
        rows.append({
            "Week": week,
            "Date Start": week_start.isoformat(),
            "Date End": week_end.isoformat(),
            "Phase": phase,
            "Objective": objective,
            "Session 1": s1,
            "Session 2": s2,
            "Session 3": s3,
            "Session 4": s4,
            "Optional Session": optional,
            "Status": "Not Started",
            "Notes": "",
        })
    return pd.DataFrame(rows, columns=TABLE_SCHEMAS["weekly_plan"])



def build_settings() -> pd.DataFrame:
    rows = [
        ["target_overall", f"{DEFAULT_TARGET_OVERALL:.1f}", "Target IELTS overall band score"],
        ["target_min_skill", f"{DEFAULT_TARGET_MIN_SKILL:.1f}", "Minimum acceptable band for each skill"],
        ["exam_date", DEFAULT_EXAM_DATE.isoformat(), "Expected IELTS exam date"],
        ["weekly_sessions", str(DEFAULT_WEEKLY_SESSIONS), "Target number of IELTS study sessions per week"],
    ]
    return pd.DataFrame(rows, columns=TABLE_SCHEMAS["settings"])


def build_task_types() -> pd.DataFrame:
    rows = []
    for skill in SKILLS:
        for task_type in DEFAULT_TASK_TYPES.get(skill, []):
            rows.append([skill, task_type, "Yes", "No", ""])
    return pd.DataFrame(rows, columns=TABLE_SCHEMAS["task_types"])


def build_resources() -> pd.DataFrame:
    rows = [
        ["Official", "IELTS Academic sample test questions", "https://ielts.org/take-a-test/preparation-resources/sample-test-questions/academic-test", "Official sample tasks and model answers", "Use first before third-party materials"],
        ["Official", "IELTS band score resources", "https://ielts.org/organisations/ielts-for-organisations/understanding-ielts-scoring/resources-for-setting-your-ielts-scores", "Writing/Speaking self-check criteria", "Use after every essay or speaking mock"],
        ["Practice", "British Council free IELTS practice tests", "https://takeielts.britishcouncil.org/take-ielts/prepare/free-ielts-english-practice-tests", "Listening/Reading/Writing practice", "Good for timed practice"],
        ["Books", "Cambridge IELTS Academic books", "Cambridge IELTS Academic recent volumes", "Main mock-test source", "Use recent volumes first"],
        ["Listening", "BBC Learning English", "https://www.bbc.co.uk/learningenglish", "General listening exposure", "Use for light practice"],
        ["Reading", "The Conversation", "https://theconversation.com/", "Academic-style reading", "Good for topic vocabulary"],
        ["Speaking", "Self-recording", "Phone recorder or laptop recorder", "Fluency and pronunciation review", "Upload recordings in Practice Workspace"],
    ]
    return pd.DataFrame(rows, columns=TABLE_SCHEMAS["resources"])


def default_table(table_name: str) -> pd.DataFrame:
    if table_name == "weekly_plan":
        return build_weekly_plan()
    if table_name == "settings":
        return build_settings()
    if table_name == "task_types":
        return build_task_types()
    if table_name == "resources":
        return build_resources()
    return pd.DataFrame(columns=TABLE_SCHEMAS[table_name])


def _clean_df(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    columns = TABLE_SCHEMAS[table_name]
    df = df.copy().fillna("")
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    return df[columns].astype(str)


def _read_local_table(table_name: str) -> pd.DataFrame:
    ensure_local_data_files()
    path = table_path(table_name)
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        df = default_table(table_name)
    return _clean_df(table_name, df)


def _save_local_table(table_name: str, df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    _clean_df(table_name, df).to_csv(table_path(table_name), index=False)


def ensure_local_data_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(exist_ok=True)
    for table_name in TABLE_SCHEMAS:
        path = table_path(table_name)
        if not path.exists():
            default_table(table_name).to_csv(path, index=False)


def _streamlit_secrets() -> dict[str, Any]:
    try:
        import streamlit as st
        return st.secrets  # type: ignore[return-value]
    except Exception:
        return {}


def get_secret_section(section: str) -> dict[str, Any]:
    secrets = _streamlit_secrets()
    try:
        value = secrets[section]
        return dict(value)
    except Exception:
        return {}


def get_storage_settings() -> dict[str, str]:
    secrets = _streamlit_secrets()
    storage = get_secret_section("storage")
    def sget(name: str, default: str = "") -> str:
        try:
            return str(storage.get(name) or secrets.get(name) or default)
        except Exception:
            return str(storage.get(name) or default)
    return {
        "google_sheet_id": sget("google_sheet_id"),
        "google_drive_folder_id": sget("google_drive_folder_id"),
    }


def cloud_configured() -> bool:
    settings = get_storage_settings()
    service_account = get_secret_section("gcp_service_account")
    return bool(settings.get("google_sheet_id") and service_account)


def drive_configured() -> bool:
    settings = get_storage_settings()
    service_account = get_secret_section("gcp_service_account")
    return bool(settings.get("google_drive_folder_id") and service_account)




def _cache_data(ttl_seconds: int):
    """Use Streamlit cache when running inside Streamlit; no-op otherwise."""
    try:
        import streamlit as st
        return st.cache_data(ttl=ttl_seconds, show_spinner=False)
    except Exception:
        def decorator(func):
            return func
        return decorator


def _cache_resource():
    """Use Streamlit resource cache when running inside Streamlit; no-op otherwise."""
    try:
        import streamlit as st
        return st.cache_resource(show_spinner=False)
    except Exception:
        def decorator(func):
            return func
        return decorator


def clear_google_cache() -> None:
    """Clear cached Google Sheet reads after a write or when the user wants a manual refresh."""
    for func_name in ["_get_spreadsheet_cached", "_get_worksheet_cached", "_read_gsheet_table_cached"]:
        func = globals().get(func_name)
        try:
            func.clear()  # type: ignore[attr-defined]
        except Exception:
            pass

def get_google_credentials(scopes: list[str]):
    service_account = get_secret_section("gcp_service_account")
    if not service_account:
        raise RuntimeError("Missing [gcp_service_account] in Streamlit secrets.")
    try:
        from google.oauth2.service_account import Credentials
    except Exception as exc:
        raise RuntimeError("google-auth is not installed. Run: pip install -r requirements.txt") from exc
    return Credentials.from_service_account_info(service_account, scopes=scopes)


def get_gspread_client():
    try:
        import gspread
    except Exception as exc:
        raise RuntimeError("gspread is not installed. Run: pip install -r requirements.txt") from exc
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    return gspread.authorize(get_google_credentials(scopes))


@_cache_resource()
def _get_spreadsheet_cached(sheet_id: str):
    return get_gspread_client().open_by_key(sheet_id)


def _get_spreadsheet():
    settings = get_storage_settings()
    sheet_id = settings.get("google_sheet_id")
    if not sheet_id:
        raise RuntimeError("Missing google_sheet_id in Streamlit secrets.")
    return _get_spreadsheet_cached(sheet_id)


@_cache_resource()
def _get_worksheet_cached(sheet_id: str, table_name: str):
    ss = _get_spreadsheet_cached(sheet_id)
    try:
        import gspread
        try:
            ws = ss.worksheet(table_name)
        except gspread.WorksheetNotFound:
            cols = max(len(TABLE_SCHEMAS[table_name]) + 3, 10)
            ws = ss.add_worksheet(title=table_name, rows=200, cols=cols)
            df = default_table(table_name)
            _write_worksheet(ws, table_name, df)
        return ws
    except Exception:
        # Some gspread versions expose WorksheetNotFound differently; try generic fallback.
        for ws in ss.worksheets():
            if ws.title == table_name:
                return ws
        cols = max(len(TABLE_SCHEMAS[table_name]) + 3, 10)
        ws = ss.add_worksheet(title=table_name, rows=200, cols=cols)
        df = default_table(table_name)
        _write_worksheet(ws, table_name, df)
        return ws


def _get_or_create_worksheet(table_name: str):
    settings = get_storage_settings()
    sheet_id = settings.get("google_sheet_id")
    if not sheet_id:
        raise RuntimeError("Missing google_sheet_id in Streamlit secrets.")
    return _get_worksheet_cached(sheet_id, table_name)


def _write_worksheet(ws, table_name: str, df: pd.DataFrame) -> None:
    df = _clean_df(table_name, df)
    payload = [TABLE_SCHEMAS[table_name]] + df.astype(str).values.tolist()
    ws.clear()
    if payload:
        ws.update(values=payload, range_name="A1")


def _read_gsheet_table_uncached(table_name: str) -> pd.DataFrame:
    ws = _get_or_create_worksheet(table_name)
    values = ws.get_all_values()
    if not values:
        df = default_table(table_name)
        _write_worksheet(ws, table_name, df)
        return _clean_df(table_name, df)
    header = values[0]
    rows = values[1:]
    if not rows:
        df = default_table(table_name)
        if not df.empty:
            _write_worksheet(ws, table_name, df)
        return _clean_df(table_name, df)
    width = len(header)
    normalized_rows = [row + [""] * max(0, width - len(row)) for row in rows]
    df = pd.DataFrame(normalized_rows, columns=header)
    return _clean_df(table_name, df)


@_cache_data(ttl_seconds=120)
def _read_gsheet_table_cached(table_name: str, sheet_id: str) -> pd.DataFrame:
    # sheet_id is part of the cache key so switching sheets does not reuse old data.
    _ = sheet_id
    return _read_gsheet_table_uncached(table_name)


def _read_gsheet_table(table_name: str) -> pd.DataFrame:
    settings = get_storage_settings()
    sheet_id = settings.get("google_sheet_id", "")
    return _read_gsheet_table_cached(table_name, sheet_id)


def _save_gsheet_table(table_name: str, df: pd.DataFrame) -> None:
    ws = _get_or_create_worksheet(table_name)
    _write_worksheet(ws, table_name, df)
    clear_google_cache()


def _warn_cloud_fallback(exc: Exception) -> None:
    try:
        import streamlit as st
        key = "_cloud_fallback_warning_shown"
        if not st.session_state.get(key):
            st.warning(f"Google Sheets/Drive is not available right now, so the app is using local CSV fallback. Details: {exc}")
            st.session_state[key] = True
    except Exception:
        pass


def ensure_data_files() -> None:
    # Keep this lightweight. Streamlit reruns pages often, so do not touch every
    # Google worksheet here; actual tables are created/read lazily when needed.
    ensure_local_data_files()


def read_table(table_name: str) -> pd.DataFrame:
    if table_name not in TABLE_SCHEMAS:
        raise KeyError(f"Unknown table: {table_name}")
    if cloud_configured():
        try:
            return _read_gsheet_table(table_name)
        except Exception as exc:
            _warn_cloud_fallback(exc)
    return _read_local_table(table_name)


def save_table(table_name: str, df: pd.DataFrame) -> None:
    if table_name not in TABLE_SCHEMAS:
        raise KeyError(f"Unknown table: {table_name}")
    if cloud_configured():
        try:
            _save_gsheet_table(table_name, df)
            return
        except Exception as exc:
            _warn_cloud_fallback(exc)
    _save_local_table(table_name, df)


def append_row(table_name: str, row: dict[str, Any]) -> None:
    if table_name not in TABLE_SCHEMAS:
        raise KeyError(f"Unknown table: {table_name}")

    cleaned_row = [str(row.get(col, "")) for col in TABLE_SCHEMAS[table_name]]

    if cloud_configured():
        try:
            ws = _get_or_create_worksheet(table_name)
            ws.append_row(cleaned_row, value_input_option="USER_ENTERED")
            clear_google_cache()
            return
        except Exception as exc:
            _warn_cloud_fallback(exc)

    df = _read_local_table(table_name)
    row_df = pd.DataFrame([{col: row.get(col, "") for col in TABLE_SCHEMAS[table_name]}])
    df = pd.concat([df, row_df], ignore_index=True)
    _save_local_table(table_name, df)


def zip_data_bytes() -> bytes:
    ensure_local_data_files()
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for table_name in TABLE_SCHEMAS:
            df = read_table(table_name)
            zf.writestr(f"data/{table_name}.csv", df.to_csv(index=False))
        if UPLOAD_DIR.exists():
            for path in UPLOAD_DIR.rglob("*"):
                if path.is_file():
                    zf.write(path, arcname=str(path.relative_to(ROOT_DIR)))
    buffer.seek(0)
    return buffer.getvalue()


def restore_backup(uploaded_file) -> list[str]:
    ensure_local_data_files()
    allowed = {f"{name}.csv" for name in TABLE_SCHEMAS}
    restored: list[str] = []
    with zipfile.ZipFile(BytesIO(uploaded_file.getvalue())) as zf:
        for item in zf.infolist():
            filename = Path(item.filename).name
            if filename in allowed:
                table_name = filename.replace(".csv", "")
                with zf.open(item) as src:
                    df = pd.read_csv(src, dtype=str).fillna("")
                save_table(table_name, df)
                restored.append(filename)
            elif item.filename.startswith("data/uploads/") and not item.is_dir():
                target = ROOT_DIR / item.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(item) as src, target.open("wb") as dst:
                    dst.write(src.read())
    return restored



def get_setting_value(settings_df: pd.DataFrame, setting: str, default: str = "") -> str:
    if settings_df.empty or "Setting" not in settings_df.columns:
        return default
    match = settings_df[settings_df["Setting"] == setting]
    if match.empty:
        return default
    value = str(match.iloc[0].get("Value", "")).strip()
    return value if value else default


def get_app_settings() -> dict[str, Any]:
    df = read_table("settings")

    def as_float(name: str, default: float) -> float:
        try:
            return float(get_setting_value(df, name, str(default)))
        except Exception:
            return default

    def as_int(name: str, default: int) -> int:
        try:
            return int(float(get_setting_value(df, name, str(default))))
        except Exception:
            return default

    exam_date_text = get_setting_value(df, "exam_date", DEFAULT_EXAM_DATE.isoformat())
    try:
        exam_date = date.fromisoformat(exam_date_text)
    except Exception:
        exam_date = DEFAULT_EXAM_DATE

    return {
        "target_overall": as_float("target_overall", DEFAULT_TARGET_OVERALL),
        "target_min_skill": as_float("target_min_skill", DEFAULT_TARGET_MIN_SKILL),
        "weekly_sessions": as_int("weekly_sessions", DEFAULT_WEEKLY_SESSIONS),
        "exam_date": exam_date,
    }


def save_app_settings(target_overall: float, target_min_skill: float, weekly_sessions: int, exam_date: date) -> None:
    rows = [
        {"Setting": "target_overall", "Value": f"{target_overall:.1f}", "Description": "Target IELTS overall band score"},
        {"Setting": "target_min_skill", "Value": f"{target_min_skill:.1f}", "Description": "Minimum acceptable band for each skill"},
        {"Setting": "exam_date", "Value": exam_date.isoformat(), "Description": "Expected IELTS exam date"},
        {"Setting": "weekly_sessions", "Value": str(int(weekly_sessions)), "Description": "Target number of IELTS study sessions per week"},
    ]
    save_table("settings", pd.DataFrame(rows, columns=TABLE_SCHEMAS["settings"]))


def get_task_type_options(skill: str) -> list[str]:
    df = read_table("task_types")
    if df.empty:
        return DEFAULT_TASK_TYPES.get(skill, [])
    view = df[(df["Skill"] == skill) & (df["Active"].str.lower().isin(["yes", "true", "1", "active"]))]
    options = [str(x).strip() for x in view["Task Type"].tolist() if str(x).strip()]
    # Preserve order while removing duplicates.
    seen = set()
    unique = []
    for option in options:
        key = option.lower()
        if key not in seen:
            seen.add(key)
            unique.append(option)
    return unique or DEFAULT_TASK_TYPES.get(skill, [])


def add_task_type(skill: str, task_type: str, notes: str = "") -> bool:
    task_type = str(task_type).strip()
    if not task_type:
        return False
    df = read_table("task_types")
    if df.empty:
        df = build_task_types()
    exists = ((df["Skill"] == skill) & (df["Task Type"].str.lower() == task_type.lower())).any()
    if exists:
        return False
    row = pd.DataFrame([{
        "Skill": skill,
        "Task Type": task_type,
        "Active": "Yes",
        "Custom": "Yes",
        "Notes": notes,
    }], columns=TABLE_SCHEMAS["task_types"])
    save_table("task_types", pd.concat([df, row], ignore_index=True))
    return True


def make_practice_id() -> str:
    return datetime.now().strftime("P%Y%m%d%H%M%S%f")[:-3]


def make_file_id() -> str:
    return datetime.now().strftime("F%Y%m%d%H%M%S%f")[:-3]


def storage_summary() -> dict[str, str]:
    settings = get_storage_settings()
    return {
        "records": "Google Sheets" if cloud_configured() else "Local CSV",
        "files": "Google Drive" if drive_configured() else "Local uploads folder",
        "google_sheet_id": settings.get("google_sheet_id", ""),
        "google_drive_folder_id": settings.get("google_drive_folder_id", ""),
        "cloud_ready": "Yes" if cloud_configured() else "No",
        "drive_ready": "Yes" if drive_configured() else "No",
    }
