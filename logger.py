import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

LOG_FILE = str(Path.home() / "GrainRock" / "grainrock_audit.log")
Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log_action(tool: str, input_data: str, result: str):
    logging.info(f"TOOL={tool} | INPUT={input_data} | RESULT={result[:150]}")

def log_question(question: str):
    logging.info(f"USER={question}")

def log_permission(action: str, granted: bool):
    status = "GRANTED" if granted else "DENIED"
    logging.info(f"PERMISSION={status} | ACTION={action}")

def log_error(error: str):
    logging.error(f"ERROR={error}")

def clean_old_logs():
    """Delete log lines older than 7 days."""
    if not os.path.exists(LOG_FILE):
        return
    cutoff = datetime.now() - timedelta(days=7)
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        recent = []
        for line in lines:
            try:
                log_date = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
                if log_date > cutoff:
                    recent.append(line)
            except:
                recent.append(line)
        with open(LOG_FILE, "w") as f:
            f.writelines(recent)
    except:
        pass