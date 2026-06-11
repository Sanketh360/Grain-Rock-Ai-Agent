import os
from pathlib import Path
from config import ALLOWED_DRIVES, ALLOWED_C_PATHS

# ─── Blocked paths — NEVER access these ──────
BLOCKED_PATHS = [
    # Windows system folders
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData",
    "C:\\System Volume Information",
    "C:\\Recovery",
    "C:\\Boot",
    "C:\\$Recycle.Bin",

    # User secret/private folders
    ".ssh",
    ".aws",
    ".gnupg",
    "AppData",
    "AppData\\Roaming",
    "AppData\\Local",
    "AppData\\LocalLow",

    # Browser data
    "Google\\Chrome\\User Data",
    "Mozilla\\Firefox\\Profiles",
    "Microsoft\\Edge\\User Data",

    # Credentials and secrets
    "Microsoft\\Credentials",
    "Microsoft\\Protect",
    ".bitcoin",
    "wallet.dat",
    "keystore",
    ".env",
    "secrets",
    "private_key",
    "id_rsa",
    "credentials",
    "password",
    "passwd",
]

# ─── Blocked file extensions ──────────────────
BLOCKED_EXTENSIONS = [
    ".pem", ".key", ".p12", ".kdbx",
    ".wallet", ".ppk", ".pfx", ".cer",
    ".crt", ".der", ".p7b", ".jks",
    ".keystore", ".asc",
]

# ─── Blocked system filenames ─────────────────
BLOCKED_FILENAMES = [
    "ntds.dit", "sam", "system",
    "security", "software", "default",
    "hiberfil.sys", "pagefile.sys",
    "swapfile.sys",
]

def is_path_safe(path: str) -> tuple[bool, str]:
    """
    Returns (True, "")        → path is safe to access
    Returns (False, reason)   → path is blocked
    
    Rules:
    - C drive blocked EXCEPT specific user folders
    - AppData always blocked even inside user folders
    - Sensitive extensions always blocked
    - System files always blocked
    """
    path_str   = str(path)
    path_upper = path_str.upper()
    path_lower = path_str.lower()
    path_obj   = Path(path_str)

    # ── Rule 1: Block AppData always ──
    # Even though Desktop/Downloads are allowed,
    # AppData inside them should never be accessed
    if "appdata" in path_lower:
        return False, "AppData is always restricted"

    # ── Rule 2: Check if on C drive ──
    if path_upper.startswith("C:\\"):
        # Check if it's one of the allowed C paths
        allowed = False
        for allowed_path in ALLOWED_C_PATHS:
            if path_upper.startswith(allowed_path):
                allowed = True
                break
        if not allowed:
            return False, "C:\\ drive is restricted (only Desktop, Downloads, Documents, Pictures, Music, Videos allowed)"

    # ── Rule 3: Check blocked path patterns ──
    for blocked in BLOCKED_PATHS:
        if blocked.lower() in path_lower:
            return False, f"Protected path: {blocked}"

    # ── Rule 4: Check blocked extensions ──
    if path_obj.suffix.lower() in BLOCKED_EXTENSIONS:
        return False, f"Protected file type: {path_obj.suffix}"

    # ── Rule 5: Check blocked filenames ──
    if path_obj.name.lower() in BLOCKED_FILENAMES:
        return False, f"Protected system file: {path_obj.name}"

    return True, ""


def is_on_allowed_drive(path: str) -> bool:
    """
    Returns True if path is on:
    - D drive (full access)
    - E drive (full access)
    - Allowed C drive user folders
    """
    path_upper = path.upper()

    # Check D and E drives
    for drive in ALLOWED_DRIVES:
        if path_upper.startswith(drive.upper()):
            return True

    # Check allowed C drive folders
    for allowed_path in ALLOWED_C_PATHS:
        if path_upper.startswith(allowed_path):
            return True

    return False


def sanitize_input(user_input: str) -> str:
    """Remove dangerous patterns from user input."""
    dangerous = [
        "../", "..\\",
        "/etc/", "/root/",
        "passwd", "shadow",
        "cmd.exe", "powershell",
        "rm -rf", "del /f",
        "format", "reg delete",
        "netsh", "regedit",
    ]
    cleaned = user_input
    for pattern in dangerous:
        cleaned = cleaned.replace(pattern, "")
    return cleaned.strip()