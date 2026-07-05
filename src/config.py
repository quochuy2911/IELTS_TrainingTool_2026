from datetime import date

APP_TITLE = "IELTS Academic Dashboard"

# These are only defaults. The app reads editable targets from the `settings` table.
DEFAULT_TARGET_OVERALL = 7.5
DEFAULT_TARGET_MIN_SKILL = 6.5
DEFAULT_WEEKLY_SESSIONS = 5
PLAN_START = date(2026, 7, 6)
PLAN_END = date(2026, 12, 31)
DEFAULT_EXAM_DATE = date(2027, 1, 15)

SKILLS = ["Listening", "Reading", "Writing", "Speaking"]
PHASES = [
    "Foundation + Diagnostic",
    "Skill Building",
    "Band 7 Development",
    "Mock Practice + Weakness Repair",
    "Final Preparation",
]

DEFAULT_TASK_TYPES = {
    "Listening": [
        "Section 1 - Daily Conversation",
        "Section 2 - Monologue",
        "Section 3 - Academic Discussion",
        "Section 4 - Lecture",
        "Full Listening Test",
        "Transcript Review",
        "Map / Plan / Diagram Labelling",
        "Multiple Choice",
        "Note / Form / Table Completion",
        "Spelling / Numbers / Plurals Drill",
    ],
    "Reading": [
        "Passage 1",
        "Passage 2",
        "Passage 3",
        "Full Academic Reading Test",
        "True / False / Not Given",
        "Yes / No / Not Given",
        "Matching Headings",
        "Matching Information / Features",
        "Sentence Completion",
        "Summary / Note / Table Completion",
        "Multiple Choice",
    ],
    "Writing": [
        "Task 1 - Line Graph",
        "Task 1 - Bar Chart",
        "Task 1 - Pie Chart",
        "Task 1 - Table",
        "Task 1 - Mixed Chart",
        "Task 1 - Process Diagram",
        "Task 1 - Map",
        "Task 2 - Opinion Essay",
        "Task 2 - Discussion Essay",
        "Task 2 - Problem/Solution Essay",
        "Task 2 - Advantages/Disadvantages Essay",
        "Rewrite / Correction",
    ],
    "Speaking": [
        "Part 1 - Short Answers",
        "Part 2 - Cue Card",
        "Part 3 - Discussion",
        "Full Speaking Mock",
        "Fluency Practice",
        "Pronunciation / Accent Review",
        "Vocabulary Expansion",
    ],
}

STATUS_OPTIONS = ["Not Started", "In Progress", "Done", "Skipped"]
BAND_OPTIONS = [""] + [f"{x/2:.1f}" for x in range(0, 19)]

IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]
AUDIO_EXTENSIONS = ["mp3", "wav", "m4a", "aac", "ogg", "flac"]
DOCUMENT_EXTENSIONS = ["pdf", "docx", "txt"]
ALLOWED_UPLOAD_EXTENSIONS = IMAGE_EXTENSIONS + AUDIO_EXTENSIONS + DOCUMENT_EXTENSIONS
