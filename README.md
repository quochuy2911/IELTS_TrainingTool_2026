# IELTS Academic Dashboard Tool V2.2

A personal Streamlit dashboard for IELTS Academic preparation. It combines planning, all-skill practice, media uploads, progress tracking, mock-test monitoring, error logging, and Google Sheets/Drive storage.

## What changed in V2.2

The app navigation was simplified from many separate pages into a clearer structure:

```text
Home
Weekly Plan
Study & Practice
Progress & Mocks
Settings & Storage
Resources
```

### Main improvements

- Combined practice workspace, practice archive, study log, speaking review, and error log into one **Study & Practice** page.
- Added skill-specific task-type lists:
  - Listening tasks appear only when Listening is selected.
  - Reading tasks appear only when Reading is selected.
  - Writing tasks appear only when Writing is selected.
  - Speaking tasks appear only when Speaking is selected.
- Added the ability to add your own custom task types from inside the app.
- Added a **Settings & Storage** page where you can edit:
  - target overall band
  - minimum skill band
  - expected exam date
  - target sessions per week
- Added persistent `settings` and `task_types` tables.
- Kept Google Sheets/Drive support with local CSV fallback.
- Kept Google Sheets read caching to reduce quota errors.

## Folder structure

```text
ielts_academic_dashboard_tool_v2_2/
├── app.py
├── pages/
│   ├── 1_Weekly_Plan.py
│   ├── 2_Study_Practice.py
│   ├── 3_Progress_Mocks.py
│   ├── 4_Settings_Storage.py
│   └── 5_Resources.py
├── src/
│   ├── config.py
│   ├── data_utils.py
│   ├── drive_utils.py
│   ├── scoring.py
│   └── ui.py
├── data/
│   ├── weekly_plan.csv
│   ├── study_log.csv
│   ├── mock_tests.csv
│   ├── error_log.csv
│   ├── practice_archive.csv
│   ├── file_metadata.csv
│   ├── settings.csv
│   ├── task_types.csv
│   └── resources.csv
├── requirements.txt
└── .streamlit/secrets.example.toml
```

## Run locally

```bash
cd ielts_academic_dashboard_tool_v2_2
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Storage behavior

The app can run in two modes:

1. **Local fallback mode**
   - Records are stored in `data/*.csv`.
   - Uploaded files are stored in `data/uploads/`.
   - Good for local testing.

2. **Cloud mode**
   - Records are stored in Google Sheets.
   - Uploaded images/audio/files are stored in Google Drive.
   - Recommended for long-term deployed use.

## Google Sheets / Drive setup

Create `.streamlit/secrets.toml` locally, based on `.streamlit/secrets.example.toml`.

```toml
[storage]
google_sheet_id = "paste_your_google_sheet_id_here"
google_drive_folder_id = "paste_your_google_drive_folder_id_here"

[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your_cert_url"
universe_domain = "googleapis.com"
```

Do not commit `.streamlit/secrets.toml` or service-account JSON files.

## Updating an existing V2.1 repo

If you are replacing an existing V2.1 project, delete these old page files first:

```text
pages/2_Practice_Workspace.py
pages/3_Practice_Archive.py
pages/4_Speaking_Review.py
pages/5_Study_Log.py
pages/6_Progress_Charts.py
pages/7_Mock_Tests.py
pages/8_Error_Log.py
pages/9_Storage_Setup.py
pages/10_Resources.py
```

Then copy the new `pages/`, `src/`, `data/settings.csv`, `data/task_types.csv`, `app.py`, and `README.md` files.

## GitHub safety

Your `.gitignore` should include:

```gitignore
.venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
*.json
data/uploads/
```

