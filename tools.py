import os
import psutil
import shutil
import platform
import subprocess
import winreg
from pathlib import Path
from datetime import datetime
from langchain_core.tools import tool
from config import ALLOWED_SEARCH_PATHS, READABLE_EXTENSIONS
from security import is_path_safe, sanitize_input, is_on_allowed_drive
from permissions import request_permission
from logger import log_action, log_permission

# ────────────────────────────────────────────
# TOOL 1 — Search file
# ────────────────────────────────────────────
@tool
def search_file(filename: str) -> str:
    """Search for a file by name across allowed drives and folders."""
    filename = sanitize_input(filename)
    granted = request_permission(
        action="Search for File",
        details=f"Grain Rock wants to search for:\n"
                f"File: {filename}\n"
                f"Locations: Desktop, Downloads, Documents,\n"
                f"Pictures, Music, Videos, D:\\ and E:\\"
    )
    log_permission("search_file", granted)
    if not granted:
        return "Permission denied by user."

    matches = []
    for base_path in ALLOWED_SEARCH_PATHS:
        base = Path(base_path)
        if not base.exists():
            continue
        try:
            for path in base.rglob(f"*{filename}*"):
                safe, _ = is_path_safe(str(path))
                if safe and is_on_allowed_drive(str(path)):
                    matches.append(str(path))
        except (PermissionError, OSError):
            continue

    result = (
        f"Found {len(matches)} file(s):\n" + "\n".join(matches[:15])
        if matches else f"No files found matching '{filename}'"
    )
    log_action("search_file", filename, result)
    return result


# ────────────────────────────────────────────
# TOOL 2 — Disk info
# ────────────────────────────────────────────
@tool
def get_disk_info(input: str = "") -> str:
    """Get disk space information for all drives."""
    granted = request_permission(
        action="Read Disk Information",
        details="Grain Rock wants to read disk space\n"
                "for D:\\ and E:\\ drives."
    )
    log_permission("get_disk_info", granted)
    if not granted:
        return "Permission denied by user."

    lines = []
    for drive in ["C:\\", "D:\\", "E:\\"]:
        try:
            d = psutil.disk_usage(drive)
            lines.append(
                f"Drive {drive}\n"
                f"  Total : {d.total//(1<<30)} GB\n"
                f"  Used  : {d.used//(1<<30)} GB\n"
                f"  Free  : {d.free//(1<<30)} GB\n"
                f"  Usage : {d.percent}%"
            )
        except:
            lines.append(f"Drive {drive}: Not available")

    result = "\n\n".join(lines)
    log_action("get_disk_info", "disk", result)
    return result


# ────────────────────────────────────────────
# TOOL 3 — RAM info
# ────────────────────────────────────────────
@tool
def get_ram_info(input: str = "") -> str:
    """Get RAM memory usage."""
    granted = request_permission(
        action="Read RAM Information",
        details="Grain Rock wants to read RAM usage."
    )
    log_permission("get_ram_info", granted)
    if not granted:
        return "Permission denied by user."

    r = psutil.virtual_memory()
    result = (
        f"RAM Information:\n"
        f"Total     : {r.total//(1<<30)} GB\n"
        f"Used      : {r.used//(1<<30)} GB\n"
        f"Available : {r.available//(1<<30)} GB\n"
        f"Usage     : {r.percent}%"
    )
    log_action("get_ram_info", "ram", result)
    return result


# ────────────────────────────────────────────
# TOOL 4 — CPU info
# ────────────────────────────────────────────
@tool
def get_cpu_info(input: str = "") -> str:
    """Get CPU usage and core information."""
    granted = request_permission(
        action="Read CPU Information",
        details="Grain Rock wants to read CPU usage and core info."
    )
    log_permission("get_cpu_info", granted)
    if not granted:
        return "Permission denied by user."

    cpu_pct  = psutil.cpu_percent(interval=1)
    cores    = psutil.cpu_count(logical=False)
    threads  = psutil.cpu_count(logical=True)
    freq     = psutil.cpu_freq()

    result = (
        f"CPU Information:\n"
        f"Physical Cores : {cores}\n"
        f"Logical Threads: {threads}\n"
        f"Current Usage  : {cpu_pct}%\n"
        f"Frequency      : {freq.current:.0f} MHz"
    )
    log_action("get_cpu_info", "cpu", result)
    return result


# ────────────────────────────────────────────
# TOOL 5 — Search application (IMPROVED)
# ────────────────────────────────────────────
@tool
def search_application(app_name: str) -> str:
    """
    Search if an application is installed on Windows.
    Checks Registry, Start Menu, PATH, AppData, common folders,
    Microsoft Store, and desktop shortcuts.
    """
    app_name_clean = sanitize_input(app_name)

    granted = request_permission(
        action="Search for Application",
        details=f"Grain Rock wants to search if:\n"
                f"App: {app_name_clean}\n"
                f"is installed. Will check:\n"
                f"• Windows Registry\n"
                f"• Start Menu shortcuts\n"
                f"• Common install folders\n"
                f"• Microsoft Store apps\n"
                f"• Desktop shortcuts"
    )
    log_permission("search_application", granted)
    if not granted:
        return "Permission denied by user."

    results = []
    app_lower = app_name_clean.lower()

    # ── 1. Check Windows PATH ──
    path_result = shutil.which(app_name_clean)
    if path_result:
        results.append(f"✅ Found in PATH: {path_result}")

    # ── 2. Check Windows Registry (installed programs) ──
    registry_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    for reg_path in registry_keys:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    sub_name = winreg.EnumKey(key, i)
                    sub_key  = winreg.OpenKey(key, sub_name)
                    try:
                        display_name, _ = winreg.QueryValueEx(
                            sub_key, "DisplayName"
                        )
                        if app_lower in display_name.lower():
                            try:
                                location, _ = winreg.QueryValueEx(
                                    sub_key, "InstallLocation"
                                )
                            except:
                                location = "Location not specified"
                            results.append(
                                f"✅ Found in Registry: {display_name}\n"
                                f"   Location: {location}"
                            )
                    except:
                        pass
                    winreg.CloseKey(sub_key)
                except:
                    continue
            winreg.CloseKey(key)
        except:
            continue

    # ── 3. Check Current User Registry ──
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        )
        for i in range(winreg.QueryInfoKey(key)[0]):
            try:
                sub_name = winreg.EnumKey(key, i)
                sub_key  = winreg.OpenKey(key, sub_name)
                try:
                    display_name, _ = winreg.QueryValueEx(
                        sub_key, "DisplayName"
                    )
                    if app_lower in display_name.lower():
                        results.append(
                            f"✅ Found (User Install): {display_name}"
                        )
                except:
                    pass
                winreg.CloseKey(sub_key)
            except:
                continue
        winreg.CloseKey(key)
    except:
        pass

    # ── 4. Check Start Menu shortcuts ──
    start_menu_paths = [
        os.path.join(
            os.environ.get("APPDATA", ""),
            "Microsoft\\Windows\\Start Menu\\Programs"
        ),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    ]
    for sm_path in start_menu_paths:
        if os.path.exists(sm_path):
            for root, dirs, files in os.walk(sm_path):
                for f in files:
                    if app_lower in f.lower() and f.endswith(".lnk"):
                        results.append(
                            f"✅ Found in Start Menu: {f}\n"
                            f"   Path: {os.path.join(root, f)}"
                        )

    # ── 5. Check common install folders ──
    common_paths = [
        f"C:\\Program Files\\{app_name_clean}",
        f"C:\\Program Files (x86)\\{app_name_clean}",
        f"D:\\{app_name_clean}",
        f"E:\\{app_name_clean}",
        os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Programs", app_name_clean
        ),
        os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            app_name_clean
        ),
    ]
    for cp in common_paths:
        if os.path.exists(cp):
            results.append(f"✅ Found folder: {cp}")

    # ── 6. Check Microsoft Store apps ──
    try:
        ps_cmd = (
            f"Get-AppxPackage | "
            f"Where-Object {{$_.Name -like '*{app_name_clean}*'}} | "
            f"Select-Object Name, InstallLocation"
        )
        ps_result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if ps_result.stdout.strip():
            lines = [
                l for l in ps_result.stdout.strip().split("\n")
                if l.strip() and "---" not in l
            ]
            for line in lines[:3]:
                if line.strip():
                    results.append(
                        f"✅ Found in Microsoft Store: {line.strip()}"
                    )
    except:
        pass

    # ── 7. Check Desktop shortcuts ──
    desktop_paths = [
        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
        r"C:\Users\Public\Desktop",
    ]
    for dp in desktop_paths:
        if os.path.exists(dp):
            for f in os.listdir(dp):
                if app_lower in f.lower():
                    results.append(
                        f"✅ Found on Desktop: {f}"
                    )

    # ── Build result ──
    if results:
        # Deduplicate
        seen = set()
        unique = []
        for r in results:
            key = r[:60]
            if key not in seen:
                seen.add(key)
                unique.append(r)
        result = (
            f"'{app_name_clean}' IS installed on your laptop:\n\n"
            + "\n\n".join(unique[:8])
        )
    else:
        result = (
            f"'{app_name_clean}' does not appear to be installed.\n"
            f"Checked: Registry, Start Menu, PATH,\n"
            f"common folders, Microsoft Store, Desktop."
        )

    log_action("search_application", app_name_clean, result[:150])
    return result


# ────────────────────────────────────────────
# TOOL 6 — System info
# ────────────────────────────────────────────
@tool
def get_system_info(input: str = "") -> str:
    """Get general system and OS information."""
    granted = request_permission(
        action="Read System Information",
        details="Grain Rock wants to read OS version,\n"
                "hostname, processor, and boot time."
    )
    log_permission("get_system_info", granted)
    if not granted:
        return "Permission denied by user."

    info      = platform.uname()
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    result = (
        f"System Information:\n"
        f"OS        : {info.system} {info.release}\n"
        f"Version   : {info.version[:60]}\n"
        f"Machine   : {info.machine}\n"
        f"Hostname  : {info.node}\n"
        f"Processor : {info.processor}\n"
        f"Boot Time : {boot_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    log_action("get_system_info", "system", result)
    return result


# ────────────────────────────────────────────
# TOOL 7 — Read file
# ────────────────────────────────────────────
@tool
def read_file(filepath: str) -> str:
    """Read content of an allowed file type."""
    filepath = sanitize_input(filepath)
    p = Path(filepath)

    safe, reason = is_path_safe(filepath)
    if not safe:
        return f"Access blocked: {reason}"
    if not is_on_allowed_drive(filepath):
        return "Access blocked: not on an allowed drive or folder."
    if p.suffix.lower() not in READABLE_EXTENSIONS:
        return f"File type '{p.suffix}' is not in the readable list."
    if not p.exists():
        return f"File not found: {filepath}"

    try:
        size_kb = p.stat().st_size // 1024
    except:
        size_kb = 0

    granted = request_permission(
        action="Read File",
        details=f"Grain Rock wants to READ:\n"
                f"File : {p.name}\n"
                f"Path : {filepath}\n"
                f"Type : {p.suffix}\n"
                f"Size : {size_kb} KB\n\n"
                f"File will only be read, NOT modified."
    )
    log_permission(f"read_file:{filepath}", granted)
    if not granted:
        return "Permission denied by user."

    try:
        text_exts = [
            ".txt", ".csv", ".py", ".js", ".html",
            ".css", ".json", ".xml", ".md",
        ]
        if p.suffix.lower() in text_exts:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(3000)
            result = f"File content (first 3000 chars):\n{content}"
        else:
            st = p.stat()
            result = (
                f"File opened:\n"
                f"Name     : {p.name}\n"
                f"Size     : {st.st_size//1024} KB\n"
                f"Modified : {datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')}\n"
                f"Type     : {p.suffix}"
            )
        log_action("read_file", filepath, result[:100])
        return result
    except Exception as e:
        return f"Could not read file: {str(e)}"


# ────────────────────────────────────────────
# TOOL 8 — Git backup before code edit
# ────────────────────────────────────────────
@tool
def git_backup_before_edit(folder_path: str) -> str:
    """Create a Git backup before AI edits any code."""
    folder_path = sanitize_input(folder_path)
    safe, reason = is_path_safe(folder_path)
    if not safe:
        return f"Access blocked: {reason}"

    granted = request_permission(
        action="Create Git Backup",
        details=f"Before editing code, Grain Rock wants to:\n"
                f"1. Initialize Git (if not exists)\n"
                f"2. Stage all current files\n"
                f"3. Create a backup commit\n"
                f"Folder: {folder_path}"
    )
    log_permission("git_backup", granted)
    if not granted:
        return "Permission denied. Git backup skipped."

    try:
        import git
        try:
            repo = git.Repo(folder_path)
        except:
            repo = git.Repo.init(folder_path)
        repo.git.add(A=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        repo.index.commit(f"Grain Rock auto-backup: {ts}")
        result = f"✅ Git backup created at {ts}"
        log_action("git_backup", folder_path, result)
        return result
    except Exception as e:
        return f"Git backup failed: {str(e)}"


# ────────────────────────────────────────────
# TOOL 9 — List running processes
# ────────────────────────────────────────────
@tool
def list_running_processes(input: str = "") -> str:
    """List currently running processes."""
    granted = request_permission(
        action="Read Running Processes",
        details="Grain Rock wants to list all\n"
                "currently running processes."
    )
    log_permission("list_processes", granted)
    if not granted:
        return "Permission denied by user."

    procs = []
    for p in psutil.process_iter(['name', 'pid', 'status']):
        try:
            procs.append(
                f"PID {p.info['pid']:5d} | "
                f"{p.info['status']:8s} | "
                f"{p.info['name']}"
            )
        except:
            pass

    result = "Running Processes:\n" + "\n".join(
        sorted(set(procs))[:30]
    )
    log_action("list_processes", "list", result[:100])
    return result


# ────────────────────────────────────────────
# TOOL 10 — Windows Settings Help (NEW)
# ────────────────────────────────────────────

# Complete settings navigation database
SETTINGS_MAP = {
    # Bluetooth
    "bluetooth": {
        "path": "Settings → Bluetooth & devices → Bluetooth",
        "shortcut": "Win + I  →  Bluetooth & devices",
        "direct": "ms-settings:bluetooth",
        "tip": "Toggle Bluetooth on/off from the top switch."
    },
    # Display
    "display": {
        "path": "Settings → System → Display",
        "shortcut": "Win + I  →  System  →  Display",
        "direct": "ms-settings:display",
        "tip": "Change resolution, brightness, night light here."
    },
    "brightness": {
        "path": "Settings → System → Display → Brightness",
        "shortcut": "Win + I  →  System  →  Display",
        "direct": "ms-settings:display",
        "tip": "Drag the brightness slider."
    },
    "resolution": {
        "path": "Settings → System → Display → Display resolution",
        "shortcut": "Win + I  →  System  →  Display",
        "direct": "ms-settings:display",
        "tip": "Scroll down to Display resolution dropdown."
    },
    "night light": {
        "path": "Settings → System → Display → Night light",
        "shortcut": "Win + I  →  System  →  Display",
        "direct": "ms-settings:nightlight",
        "tip": "Reduces blue light in the evening."
    },
    # Sound
    "sound": {
        "path": "Settings → System → Sound",
        "shortcut": "Win + I  →  System  →  Sound",
        "direct": "ms-settings:sound",
        "tip": "Adjust volume, output device, input device."
    },
    "volume": {
        "path": "Settings → System → Sound → Volume",
        "shortcut": "Win + I  →  System  →  Sound",
        "direct": "ms-settings:sound",
        "tip": "Or press the speaker icon in the taskbar."
    },
    "microphone": {
        "path": "Settings → System → Sound → Input",
        "shortcut": "Win + I  →  System  →  Sound",
        "direct": "ms-settings:sound",
        "tip": "Select input device and test microphone."
    },
    # WiFi / Network
    "wifi": {
        "path": "Settings → Network & internet → Wi-Fi",
        "shortcut": "Win + I  →  Network & internet  →  Wi-Fi",
        "direct": "ms-settings:network-wifi",
        "tip": "Toggle WiFi and manage saved networks."
    },
    "network": {
        "path": "Settings → Network & internet",
        "shortcut": "Win + I  →  Network & internet",
        "direct": "ms-settings:network",
        "tip": "Manage all network connections."
    },
    "vpn": {
        "path": "Settings → Network & internet → VPN",
        "shortcut": "Win + I  →  Network & internet  →  VPN",
        "direct": "ms-settings:network-vpn",
        "tip": "Add and connect to VPN profiles."
    },
    "airplane mode": {
        "path": "Settings → Network & internet → Airplane mode",
        "shortcut": "Win + I  →  Network & internet  →  Airplane mode",
        "direct": "ms-settings:network-airplanemode",
        "tip": "Disables all wireless connections."
    },
    # Battery / Power
    "battery": {
        "path": "Settings → System → Power & battery",
        "shortcut": "Win + I  →  System  →  Power & battery",
        "direct": "ms-settings:batterysaver",
        "tip": "View battery usage and set battery saver."
    },
    "power": {
        "path": "Settings → System → Power & battery",
        "shortcut": "Win + I  →  System  →  Power & battery",
        "direct": "ms-settings:powersleep",
        "tip": "Set sleep timeout and power mode."
    },
    "sleep": {
        "path": "Settings → System → Power & battery → Screen and sleep",
        "shortcut": "Win + I  →  System  →  Power & battery",
        "direct": "ms-settings:powersleep",
        "tip": "Set how long before screen turns off."
    },
    # Keyboard / Mouse
    "keyboard": {
        "path": "Settings → Bluetooth & devices → Keyboard",
        "shortcut": "Win + I  →  Bluetooth & devices  →  Keyboard",
        "direct": "ms-settings:devicesinput",
        "tip": "Adjust keyboard settings and shortcuts."
    },
    "mouse": {
        "path": "Settings → Bluetooth & devices → Mouse",
        "shortcut": "Win + I  →  Bluetooth & devices  →  Mouse",
        "direct": "ms-settings:mousetouchpad",
        "tip": "Adjust pointer speed, button config."
    },
    "touchpad": {
        "path": "Settings → Bluetooth & devices → Touchpad",
        "shortcut": "Win + I  →  Bluetooth & devices  →  Touchpad",
        "direct": "ms-settings:devices-touchpad",
        "tip": "Adjust touchpad sensitivity and gestures."
    },
    # Camera
    "camera": {
        "path": "Settings → Bluetooth & devices → Camera",
        "shortcut": "Win + I  →  Bluetooth & devices  →  Camera",
        "direct": "ms-settings:camera",
        "tip": "Manage connected cameras."
    },
    # Notifications
    "notifications": {
        "path": "Settings → System → Notifications",
        "shortcut": "Win + I  →  System  →  Notifications",
        "direct": "ms-settings:notifications",
        "tip": "Control app notifications and Focus assist."
    },
    # Storage
    "storage": {
        "path": "Settings → System → Storage",
        "shortcut": "Win + I  →  System  →  Storage",
        "direct": "ms-settings:storagesense",
        "tip": "View storage usage and run Storage Sense."
    },
    # Apps
    "apps": {
        "path": "Settings → Apps → Installed apps",
        "shortcut": "Win + I  →  Apps",
        "direct": "ms-settings:appsfeatures",
        "tip": "View, modify, or uninstall installed apps."
    },
    "default apps": {
        "path": "Settings → Apps → Default apps",
        "shortcut": "Win + I  →  Apps  →  Default apps",
        "direct": "ms-settings:defaultapps",
        "tip": "Set default browser, email, media player."
    },
    "startup apps": {
        "path": "Settings → Apps → Startup",
        "shortcut": "Win + I  →  Apps  →  Startup",
        "direct": "ms-settings:startupapps",
        "tip": "Enable or disable apps that run on startup."
    },
    # Accounts
    "accounts": {
        "path": "Settings → Accounts",
        "shortcut": "Win + I  →  Accounts",
        "direct": "ms-settings:accounts",
        "tip": "Manage user accounts and sign-in options."
    },
    "password": {
        "path": "Settings → Accounts → Sign-in options",
        "shortcut": "Win + I  →  Accounts  →  Sign-in options",
        "direct": "ms-settings:signinoptions",
        "tip": "Change password, PIN, Windows Hello."
    },
    "pin": {
        "path": "Settings → Accounts → Sign-in options → PIN",
        "shortcut": "Win + I  →  Accounts  →  Sign-in options",
        "direct": "ms-settings:signinoptions",
        "tip": "Set up or change your Windows PIN."
    },
    # Privacy
    "privacy": {
        "path": "Settings → Privacy & security",
        "shortcut": "Win + I  →  Privacy & security",
        "direct": "ms-settings:privacy",
        "tip": "Control app permissions and privacy settings."
    },
    "location": {
        "path": "Settings → Privacy & security → Location",
        "shortcut": "Win + I  →  Privacy & security  →  Location",
        "direct": "ms-settings:privacy-location",
        "tip": "Allow or block apps from using your location."
    },
    # Windows Update
    "update": {
        "path": "Settings → Windows Update",
        "shortcut": "Win + I  →  Windows Update",
        "direct": "ms-settings:windowsupdate",
        "tip": "Check for and install Windows updates."
    },
    "windows update": {
        "path": "Settings → Windows Update",
        "shortcut": "Win + I  →  Windows Update",
        "direct": "ms-settings:windowsupdate",
        "tip": "Keep Windows up to date."
    },
    # Language
    "language": {
        "path": "Settings → Time & language → Language & region",
        "shortcut": "Win + I  →  Time & language  →  Language & region",
        "direct": "ms-settings:regionlanguage",
        "tip": "Add or change display language."
    },
    "date time": {
        "path": "Settings → Time & language → Date & time",
        "shortcut": "Win + I  →  Time & language  →  Date & time",
        "direct": "ms-settings:dateandtime",
        "tip": "Set time zone and sync the clock."
    },
    # Accessibility
    "accessibility": {
        "path": "Settings → Accessibility",
        "shortcut": "Win + I  →  Accessibility",
        "direct": "ms-settings:easeofaccess",
        "tip": "Vision, hearing, and interaction settings."
    },
    "magnifier": {
        "path": "Settings → Accessibility → Magnifier",
        "shortcut": "Win + I  →  Accessibility  →  Magnifier",
        "direct": "ms-settings:easeofaccess-magnifier",
        "tip": "Zoom in on parts of the screen."
    },
    # Taskbar
    "taskbar": {
        "path": "Settings → Personalization → Taskbar",
        "shortcut": "Win + I  →  Personalization  →  Taskbar",
        "direct": "ms-settings:taskbar",
        "tip": "Customize taskbar position, icons, and behavior."
    },
    # Wallpaper / Theme
    "wallpaper": {
        "path": "Settings → Personalization → Background",
        "shortcut": "Win + I  →  Personalization  →  Background",
        "direct": "ms-settings:personalization-background",
        "tip": "Change desktop wallpaper or slideshow."
    },
    "theme": {
        "path": "Settings → Personalization → Themes",
        "shortcut": "Win + I  →  Personalization  →  Themes",
        "direct": "ms-settings:themes",
        "tip": "Apply Windows themes including dark mode."
    },
    "dark mode": {
        "path": "Settings → Personalization → Colors",
        "shortcut": "Win + I  →  Personalization  →  Colors",
        "direct": "ms-settings:colors",
        "tip": "Switch between Light and Dark mode."
    },
}


@tool
def get_windows_settings_help(setting_query: str) -> str:
    """
    Get exact navigation instructions for any Windows Setting.
    Use when user asks where to find Bluetooth, Display,
    WiFi, Sound, Battery, or any other setting.
    """
    query_lower = setting_query.lower().strip()

    # Find best match
    best_match = None
    best_score = 0

    for key, data in SETTINGS_MAP.items():
        # Exact match
        if key == query_lower:
            best_match = (key, data)
            break
        # Partial match
        if key in query_lower or query_lower in key:
            score = len(key)
            if score > best_score:
                best_score = score
                best_match = (key, data)
        # Word match
        for word in query_lower.split():
            if word in key and len(word) > 3:
                score = len(word)
                if score > best_score:
                    best_score = score
                    best_match = (key, data)

    if best_match:
        name, info = best_match
        result = (
            f"📍 How to find '{name.title()}' in Windows Settings:\n\n"
            f"📌 Navigation Path:\n"
            f"   {info['path']}\n\n"
            f"⌨️  Keyboard Shortcut:\n"
            f"   {info['shortcut']}\n\n"
            f"🚀 Quick Open (copy & run in Run dialog Win+R):\n"
            f"   {info['direct']}\n\n"
            f"💡 Tip:\n"
            f"   {info['tip']}"
        )
    else:
        # Generic guidance
        result = (
            f"📍 To find '{setting_query}' in Windows Settings:\n\n"
            f"1. Press  Win + I  to open Settings\n"
            f"2. Use the Search bar at the top\n"
            f"3. Type '{setting_query}' to find it\n\n"
            f"Or press  Win + S  and search for the setting directly.\n\n"
            f"Common settings locations:\n"
            f"• System settings  →  Win+I → System\n"
            f"• Device settings  →  Win+I → Bluetooth & devices\n"
            f"• Network settings →  Win+I → Network & internet\n"
            f"• App settings     →  Win+I → Apps\n"
            f"• Privacy settings →  Win+I → Privacy & security"
        )

    log_action("settings_help", setting_query, result[:100])
    return result