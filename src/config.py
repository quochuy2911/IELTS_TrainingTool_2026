from datetime import date

APP_TITLE = "IELTS Academic Dashboard"
TARGET_OVERALL = 7.5
TARGET_MIN_SKILL = 6.5
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

TASK_TYPES = {
    "Listening": [
        "Section 1", "Section 2", "Section 3", "Section 4", "Full Listening Test",
        "Transcript Review", "Map/Diagram", "Multiple Choice", "Note Completion"
    ],
    "Reading": [
        "Passage 1", "Passage 2", "Passage 3", "Full Academic Reading Test",
        "True/False/Not Given", "Matching Headings", "Sentence Completion", "Multiple Choice"
    ],
    "Writing": [
        "Academic Task 1 - Line/Bar/Pie/Table", "Academic Task 1 - Process/Map",
        "Academic Task 1 - Mixed Chart", "Task 2 - Opinion Essay", "Task 2 - Discussion Essay",
        "Task 2 - Problem/Solution", "Task 2 - Advantages/Disadvantages", "Rewrite/Correction"
    ],
    "Speaking": [
        "Part 1", "Part 2 Cue Card", "Part 3", "Full Speaking Mock",
        "Vocabulary Practice", "Pronunciation/Fluency Review"
    ],
}

STATUS_OPTIONS = ["Not Started", "In Progress", "Done", "Skipped"]
BAND_OPTIONS = [""] + [f"{x/2:.1f}" for x in range(0, 19)]

IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]
AUDIO_EXTENSIONS = ["mp3", "wav", "m4a", "aac", "ogg", "flac"]
DOCUMENT_EXTENSIONS = ["pdf", "docx", "txt"]
ALLOWED_UPLOAD_EXTENSIONS = IMAGE_EXTENSIONS + AUDIO_EXTENSIONS + DOCUMENT_EXTENSIONS
