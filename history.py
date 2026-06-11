import json
import os
from pathlib import Path
from datetime import datetime
from config import HISTORY_FILE, MAX_HISTORY

def _ensure_history_dir():
    Path(HISTORY_FILE).parent.mkdir(parents=True, exist_ok=True)

def save_message(role: str, content: str):
    """Save a single message to history file."""
    _ensure_history_dir()
    history = load_history()
    history.append({
        "role"     : role,
        "content"  : content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # Keep only last MAX_HISTORY messages
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def load_history() -> list:
    """Load all history from file."""
    _ensure_history_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def delete_history():
    """Delete all chat history."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

def delete_ai_memory():
    """
    Delete history AND reset conversation memory.
    This clears everything AI knows about past chats.
    """
    delete_history()
    memory_files = [
        str(Path.home() / "GrainRock" / "memory.json"),
        str(Path.home() / "GrainRock" / "context.json"),
    ]
    for f in memory_files:
        if os.path.exists(f):
            os.remove(f)
    return True