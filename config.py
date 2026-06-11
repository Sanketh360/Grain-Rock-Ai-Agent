import os
from pathlib import Path

# ─── App Info ────────────────────────────────
APP_NAME        = "Grain Rock"
APP_VERSION     = "2.0.0"
APP_WIDTH       = 1000
APP_HEIGHT      = 700

# ─── AI Model ────────────────────────────────
OLLAMA_MODEL    = "qwen2.5:7b"
OLLAMA_BASE_URL = "http://localhost:11434"

# ─── Ollama exe ───────────────────────────────
USERNAME  = os.environ.get("USERNAME", "")
OLLAMA_EXE = (
    f"C:\\Users\\{USERNAME}\\"
    f"AppData\\Local\\Programs\\Ollama\\ollama.exe"
)

# ─── User home ────────────────────────────────
HOME = str(Path.home())

# ─── Allowed C drive user folders ────────────
ALLOWED_C_PATHS = [
    os.path.join(HOME, "Desktop").upper(),
    os.path.join(HOME, "Downloads").upper(),
    os.path.join(HOME, "Documents").upper(),
    os.path.join(HOME, "Pictures").upper(),
    os.path.join(HOME, "Music").upper(),
    os.path.join(HOME, "Videos").upper(),
]

# ─── Allowed drives ───────────────────────────
ALLOWED_DRIVES = ["D:\\", "E:\\"]

# ─── All allowed search paths ─────────────────
ALLOWED_SEARCH_PATHS = [
    os.path.join(HOME, "Desktop"),
    os.path.join(HOME, "Downloads"),
    os.path.join(HOME, "Documents"),
    os.path.join(HOME, "Pictures"),
    os.path.join(HOME, "Music"),
    os.path.join(HOME, "Videos"),
    "D:\\",
    "E:\\",
]

# ─── Readable file types ──────────────────────
READABLE_EXTENSIONS = [
    ".pdf", ".txt", ".csv", ".doc", ".docx",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".py", ".js", ".html", ".css", ".json",
    ".xml", ".md", ".xlsx", ".pptx", ".java",".dart",".kt",
    ".mp3", ".mp4", ".avi", ".mkv",
]

# ─── History file ─────────────────────────────
HISTORY_FILE        = "D:\\GrainRock\\history.json"
MAX_HISTORY         = 500

# ─── Session timeout (minutes) ────────────────
SESSION_TIMEOUT     = 15

# ─── Ollama startup wait (seconds) ────────────
OLLAMA_WAIT_SECONDS = 20