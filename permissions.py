import customtkinter as ctk
from typing import Callable

class PermissionDialog(ctk.CTkToplevel):
    """
    Shows a permission popup asking user
    to Allow or Deny an AI action.
    """
    def __init__(
        self,
        parent,
        action: str,
        details: str,
        callback: Callable[[bool], None]
    ):
        super().__init__(parent)
        self.callback = callback
        self.result   = False

        # Window setup
        self.title("⚠️ Permission Required")
        self.geometry("500x320")
        self.resizable(False, False)
        self.grab_set()  # Modal window
        self.lift()
        self.focus_force()

        # Make it appear on top
        self.attributes("-topmost", True)

        self._build_ui(action, details)

    def _build_ui(self, action: str, details: str):
        # Warning icon and title
        title_label = ctk.CTkLabel(
            self,
            text="⚠️  Grain Rock Needs Permission",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="orange"
        )
        title_label.pack(pady=(20, 5))

        # What AI wants to do
        action_label = ctk.CTkLabel(
            self,
            text=f"Action: {action}",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        action_label.pack(pady=(5, 5), padx=20)

        # Details box
        details_box = ctk.CTkTextbox(
            self,
            height=100,
            font=ctk.CTkFont(size=13),
            wrap="word",
        )
        details_box.insert("1.0", details)
        details_box.configure(state="disabled")
        details_box.pack(fill="x", padx=20, pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        allow_btn = ctk.CTkButton(
            btn_frame,
            text="✅ Allow",
            width=150,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen",
            command=self._allow
        )
        allow_btn.pack(side="left", padx=10)

        deny_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Deny",
            width=150,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red",
            hover_color="darkred",
            command=self._deny
        )
        deny_btn.pack(side="left", padx=10)

    def _allow(self):
        self.result = True
        self.callback(True)
        self.destroy()

    def _deny(self):
        self.result = False
        self.callback(False)
        self.destroy()


# ─── Global permission request function ──────
_main_window = None

def set_main_window(window):
    global _main_window
    _main_window = window

def request_permission(action: str, details: str) -> bool:
    """
    Blocks until user clicks Allow or Deny.
    Returns True if allowed, False if denied.
    """
    import threading
    result = [False]
    event  = threading.Event()

    def callback(allowed: bool):
        result[0] = allowed
        event.set()

    def show_dialog():
        PermissionDialog(_main_window, action, details, callback)

    if _main_window:
        _main_window.after(0, show_dialog)
        event.wait(timeout=60)  # 60 second timeout

    return result[0]