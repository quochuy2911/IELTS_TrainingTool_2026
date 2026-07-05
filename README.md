# IELTS Academic Dashboard Tool V2

A personal Streamlit dashboard for preparing for the IELTS Academic exam from July 2026 to January 2027.

This version is designed as a complete IELTS workspace:

- 26-week IELTS Academic study plan
- practice workspace for writing/speaking/reading/listening records
- image upload for graphs, screenshots, and prompts
- audio upload for speaking recordings
- practice archive with attachment preview
- speaking review page with audio playback and feedback editing
- study log
- progress charts
- mock test tracker
- error log
- resources page
- Google Sheets storage for records
- Google Drive storage for uploaded files
- local CSV/upload fallback for testing

---

## 1. Run locally first

```bash
cd ielts_academic_dashboard_tool_v2
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Without Google credentials, the app uses local storage:

- `data/*.csv` for records
- `data/uploads/` for uploaded files

This is good for testing, but not ideal for long-term cloud deployment.

---

## 2. Recommended deployment storage

For serious 6-month use after deploying, use:

| Data type | Recommended storage |
|---|---|
| Weekly plan status | Google Sheets |
| Study log | Google Sheets |
| Practice archive | Google Sheets |
| Mock tests | Google Sheets |
| Error log | Google Sheets |
| File metadata | Google Sheets |
| Images/audio/PDF files | Google Drive |

The app automatically uses Google Sheets/Drive when credentials are configured. Otherwise, it falls back to local files.

---

## 3. Create Google storage

### A. Create one Google Sheet

Create a blank Google Sheet, for example:

```text
IELTS Academic Dashboard Data
```

Copy the Sheet ID from the URL:

```text
https://docs.google.com/spreadsheets/d/<THIS_IS_THE_SHEET_ID>/edit
```

The app will automatically create these worksheets:

```text
weekly_plan
study_log
mock_tests
error_log
practice_archive
file_metadata
resources
```

### B. Create one Google Drive folder

Create a Google Drive folder, for example:

```text
IELTS Dashboard Uploads
```

Copy the folder ID from the URL:

```text
https://drive.google.com/drive/folders/<THIS_IS_THE_FOLDER_ID>
```

---

## 4. Create a Google Cloud service account

1. Open Google Cloud Console.
2. Create or choose a project.
3. Enable these APIs:
   - Google Sheets API
   - Google Drive API
4. Create a service account.
5. Create a JSON key for that service account.
6. Copy the service account email address.
7. Share your Google Sheet with the service account email as **Editor**.
8. Share your Google Drive upload folder with the service account email as **Editor**.

---

## 5. Configure Streamlit secrets

For local testing, copy:

```text
.streamlit/secrets.example.toml
```

to:

```text
.streamlit/secrets.toml
```

Then fill in your Google Sheet ID, Drive folder ID, and service account JSON fields.

For Streamlit Community Cloud, paste the same TOML content into:

```text
App settings > Secrets
```

Never commit your real `.streamlit/secrets.toml` to GitHub.

---

## 6. Deploy to GitHub + Streamlit Community Cloud

1. Create a GitHub repository.
2. Push this project folder to the repository.
3. Go to Streamlit Community Cloud.
4. Create a new app from your GitHub repo.
5. Set the main file path to:

```text
app.py
```

6. Add your secrets in the Streamlit app settings.
7. Deploy.
8. Open the **Storage Setup** page and test the connection.

---

## 7. App pages

```text
Home
Weekly Plan
Practice Workspace
Practice Archive
Speaking Review
Study Log
Progress Charts
Mock Tests
Error Log
Storage Setup
Resources
```

---

## 8. Recommended workflow

### For Writing Task 1

1. Open Practice Workspace.
2. Select Writing.
3. Select Academic Task 1 type.
4. Upload the chart/screenshot.
5. Write your report.
6. Save estimated band, feedback, and reflection.

### For Writing Task 2

1. Paste the prompt.
2. Write the essay.
3. Add feedback and rewrite notes.
4. Save to archive.

### For Speaking

1. Record yourself using your phone/laptop.
2. Upload the audio file.
3. Paste the question/cue card.
4. Add script/transcript or key notes.
5. Review it later in Speaking Review.

### For Reading/Listening

1. Save source/test information.
2. Add score/accuracy.
3. Add mistake pattern and fix strategy.
4. Link repeated issues to Error Log.

---

## 9. Backup

The sidebar includes a backup download button. It exports all current record tables into a ZIP file. If you are using local uploads, local uploaded files are also included.

Even with Google Sheets/Drive, it is still a good idea to download backups regularly.

---

## 10. Notes

This is a personal productivity tool, not an official IELTS scoring system. Use it to organize your preparation, store practice work, and track progress. For final score prediction, rely on repeated full mock tests and official band descriptor criteria.


## V2.1 quota-safety update

This version reduces Google Sheets API usage by:

- caching Google Sheet reads for 120 seconds;
- lazily checking/creating worksheets only when a table is needed;
- appending new rows directly instead of reading and rewriting full sheets;
- preparing data backups only when you click **Prepare backup download**;
- adding a **Refresh Google data** sidebar button for manual cache refresh.

If you see a temporary `429` quota message, stop rapid page switching, wait for the Google Sheets per-minute quota to refill, then use **Refresh Google data**.
