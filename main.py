import os
import time
import threading
import subprocess
import urllib.request
import tkinter as tk
import customtkinter as ctk

from agent import load_agent, ask_agent
from history import (
    save_message, load_history,
    delete_history, delete_ai_memory
)
from permissions import set_main_window
from logger import clean_old_logs, log_error, log_action
from config import (
    APP_NAME, APP_VERSION,
    APP_WIDTH, APP_HEIGHT,
    SESSION_TIMEOUT, OLLAMA_EXE,
    OLLAMA_BASE_URL, OLLAMA_WAIT_SECONDS,
    OLLAMA_MODEL
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Design Tokens ──────────────────────────────
BG_DARK        = "#0f0f11"
BG_PANEL       = "#1a1a1f"
BG_INPUT       = "#212128"
BG_MSG_USER    = "#1e3a5f"
BG_MSG_AI      = "#1c1c24"
ACCENT         = "#7c6ef7"
ACCENT_HOVER   = "#9d93f9"
ACCENT_STOP    = "#e05c5c"
ACCENT_STOP_H  = "#f07070"
TEXT_PRIMARY   = "#e8e8f0"
TEXT_SECONDARY = "#7070a0"
TEXT_USER      = "#c8d8f0"
TEXT_AI        = "#d0d0e8"
BORDER         = "#2a2a38"
GREEN          = "#4caf82"
ORANGE         = "#f0a050"
RED            = "#e05c5c"


class MessageBubble(ctk.CTkFrame):
    """Single chat bubble for user or AI messages."""

    def __init__(self, parent, role, content,
                 timestamp="", on_edit=None, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self.role    = role
        self.content = content
        self.on_edit = on_edit
        self._build(role, content, timestamp)

    def _build(self, role, content, timestamp):
        is_user = (role == "user")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(3, 3))

        if is_user:
            # ── User bubble — right side ──
            ctk.CTkFrame(
                row, fg_color="transparent"
            ).pack(side="left", fill="x", expand=True)

            card = ctk.CTkFrame(
                row, fg_color=BG_MSG_USER,
                corner_radius=16,
                border_width=1,
                border_color="#2a4a80"
            )
            card.pack(side="right", padx=(80, 0))

            ctk.CTkLabel(
                card, text="You",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#88aadd"
            ).pack(anchor="w", padx=14, pady=(10, 0))

            ctk.CTkLabel(
                card, text=content,
                font=ctk.CTkFont(size=13),
                text_color=TEXT_USER,
                wraplength=480, justify="left", anchor="w"
            ).pack(anchor="w", padx=14, pady=(2, 6), fill="x")

            foot = ctk.CTkFrame(card, fg_color="transparent")
            foot.pack(fill="x", padx=14, pady=(0, 8))

            if timestamp:
                ctk.CTkLabel(
                    foot, text=timestamp,
                    font=ctk.CTkFont(size=10),
                    text_color=TEXT_SECONDARY
                ).pack(side="left")

            if self.on_edit:
                ctk.CTkButton(
                    foot, text="✏️ Edit",
                    width=62, height=22,
                    font=ctk.CTkFont(size=11),
                    fg_color="transparent",
                    hover_color=BG_INPUT,
                    text_color=TEXT_SECONDARY,
                    border_width=1,
                    border_color=BORDER,
                    corner_radius=8,
                    command=lambda: self.on_edit(self.content)
                ).pack(side="right")

        else:
            # ── AI bubble — left side with icon ──
            icon_wrap = ctk.CTkFrame(
                row, fg_color=ACCENT,
                corner_radius=13, width=26, height=26
            )
            icon_wrap.pack(
                side="left", padx=(0, 8), anchor="n", pady=(4, 0)
            )
            icon_wrap.pack_propagate(False)
            ctk.CTkLabel(
                icon_wrap, text="⚡",
                font=ctk.CTkFont(size=12),
                width=26, height=26
            ).pack(expand=True)

            card = ctk.CTkFrame(
                row, fg_color=BG_MSG_AI,
                corner_radius=16,
                border_width=1,
                border_color=BORDER
            )
            card.pack(side="left", padx=(0, 80))

            ctk.CTkLabel(
                card, text="Grain Rock",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=ACCENT
            ).pack(anchor="w", padx=14, pady=(10, 0))

            ctk.CTkLabel(
                card, text=content,
                font=ctk.CTkFont(size=13),
                text_color=TEXT_AI,
                wraplength=480, justify="left", anchor="w"
            ).pack(anchor="w", padx=14, pady=(2, 6), fill="x")

            if timestamp:
                ctk.CTkLabel(
                    card, text=timestamp,
                    font=ctk.CTkFont(size=10),
                    text_color=TEXT_SECONDARY
                ).pack(anchor="w", padx=14, pady=(0, 8))


class LoadingBubble(ctk.CTkFrame):
    """Animated dots shown while AI is thinking."""

    FRAMES = [
        "Thinking  ●○○",
        "Thinking  ○●○",
        "Thinking  ○○●",
        "Thinking  ●●○",
        "Thinking  ○●●",
        "Thinking  ●○●",
    ]

    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self._running = True
        self._frame_idx = 0
        self._build()
        self._tick()

    def _build(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(3, 3))

        icon_wrap = ctk.CTkFrame(
            row, fg_color=ACCENT,
            corner_radius=13, width=26, height=26
        )
        icon_wrap.pack(
            side="left", padx=(0, 8), anchor="n", pady=(4, 0)
        )
        icon_wrap.pack_propagate(False)
        ctk.CTkLabel(
            icon_wrap, text="⚡",
            font=ctk.CTkFont(size=12), width=26, height=26
        ).pack(expand=True)

        card = ctk.CTkFrame(
            row, fg_color=BG_MSG_AI,
            corner_radius=16, border_width=1, border_color=BORDER
        )
        card.pack(side="left")

        ctk.CTkLabel(
            card, text="Grain Rock",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ACCENT
        ).pack(anchor="w", padx=14, pady=(10, 0))

        self._dot_label = ctk.CTkLabel(
            card, text=self.FRAMES[0],
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY
        )
        self._dot_label.pack(anchor="w", padx=14, pady=(2, 14))

    def _tick(self):
        if not self._running:
            return
        self._frame_idx = (self._frame_idx + 1) % len(self.FRAMES)
        try:
            self._dot_label.configure(
                text=self.FRAMES[self._frame_idx]
            )
            self.after(380, self._tick)
        except:
            pass

    def stop(self):
        self._running = False


class GrainRockApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.configure(fg_color=BG_DARK)
        self.title(f"{APP_NAME}  v{APP_VERSION}")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(True, True)
        self.minsize(760, 560)

        self.agent            = None
        self.last_activity    = time.time()
        self.locked           = False
        self._stop_event      = threading.Event()
        self._loading_bubble  = None
        self._msg_widgets     = []

        set_main_window(self)
        clean_old_logs()
        self._build_ui()
        self._load_history_to_chat()

        threading.Thread(
            target=self._startup_sequence, daemon=True
        ).start()
        self._start_timeout_checker()

    # ═══════════════════════════════════════════
    # UI BUILD
    # ═══════════════════════════════════════════

    def _build_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ──────────────────────────────
        hdr = ctk.CTkFrame(
            self, fg_color=BG_PANEL,
            corner_radius=0, height=56
        )
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)

        logo = ctk.CTkFrame(hdr, fg_color="transparent")
        logo.grid(row=0, column=0, padx=18, pady=10, sticky="w")

        ctk.CTkLabel(
            logo, text="⚡",
            font=ctk.CTkFont(size=20), text_color=ACCENT
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            logo, text="GRAIN ROCK",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkLabel(
            logo, text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY
        ).pack(side="left", padx=(6, 0), pady=(4, 0))

        self.status_label = ctk.CTkLabel(
            hdr, text="● Starting...",
            font=ctk.CTkFont(size=12),
            text_color=ORANGE
        )
        self.status_label.grid(
            row=0, column=2, padx=18, sticky="e"
        )

        # ── Toolbar ─────────────────────────────
        toolbar = ctk.CTkFrame(
            self, fg_color=BG_PANEL,
            corner_radius=0, height=48
        )
        toolbar.grid(row=1, column=0, sticky="ew")
        toolbar.grid_propagate(False)

        ctk.CTkFrame(
            toolbar, fg_color=BORDER,
            height=1, corner_radius=0
        ).pack(side="top", fill="x")

        _btn = dict(
            height=30, font=ctk.CTkFont(size=12),
            fg_color="transparent", hover_color=BG_INPUT,
            text_color=TEXT_SECONDARY,
            border_width=1, border_color=BORDER, corner_radius=8
        )
        ctk.CTkButton(
            toolbar, text="🗑  History", width=110,
            command=self._confirm_delete_history, **_btn
        ).pack(side="left", padx=(12, 4), pady=9)

        ctk.CTkButton(
            toolbar, text="🧠 Memory", width=110,
            command=self._confirm_delete_memory, **_btn
        ).pack(side="left", padx=4, pady=9)

        ctk.CTkButton(
            toolbar, text="🔒 Lock", width=90,
            command=self._lock_app, **_btn
        ).pack(side="left", padx=4, pady=9)

        ctk.CTkButton(
            toolbar, text="🔄 Restart", width=100,
            command=self._restart_ollama, **_btn
        ).pack(side="left", padx=4, pady=9)

        # ── Chat area ───────────────────────────
        chat_outer = ctk.CTkFrame(
            self, fg_color=BG_DARK, corner_radius=0
        )
        chat_outer.grid(row=2, column=0, sticky="nsew")

        self._canvas = tk.Canvas(
            chat_outer, bg=BG_DARK,
            highlightthickness=0, bd=0
        )
        _sb = ctk.CTkScrollbar(
            chat_outer,
            command=self._canvas.yview,
            fg_color=BG_DARK,
            button_color=BG_PANEL,
            button_hover_color=BORDER
        )
        self._canvas.configure(yscrollcommand=_sb.set)
        _sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._msgs_frame = ctk.CTkFrame(
            self._canvas, fg_color=BG_DARK, corner_radius=0
        )
        self._win_id = self._canvas.create_window(
            (0, 0), window=self._msgs_frame, anchor="nw"
        )

        self._msgs_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            )
        )
        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfig(
                self._win_id, width=e.width
            )
        )
        self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(
                int(-1*(e.delta/120)), "units"
            )
        )

        # ── Input area ──────────────────────────
        inp_outer = ctk.CTkFrame(
            self, fg_color=BG_PANEL, corner_radius=0
        )
        inp_outer.grid(row=3, column=0, sticky="ew")

        ctk.CTkFrame(
            inp_outer, fg_color=BORDER,
            height=1, corner_radius=0
        ).pack(fill="x")

        inp_row = ctk.CTkFrame(
            inp_outer, fg_color="transparent"
        )
        inp_row.pack(fill="x", padx=14, pady=10)

        self.input_box = ctk.CTkTextbox(
            inp_row, height=46,
            font=ctk.CTkFont(size=14),
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            corner_radius=12,
            text_color=TEXT_PRIMARY,
            wrap="word"
        )
        self.input_box.pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self.input_box.bind("<Return>", self._enter_key)
        self.input_box.bind("<Shift-Return>", lambda e: None)

        btns = ctk.CTkFrame(inp_row, fg_color="transparent")
        btns.pack(side="right")

        # Stop button
        self.stop_btn = ctk.CTkButton(
            btns, text="⏹",
            width=46, height=46,
            font=ctk.CTkFont(size=18),
            fg_color=BG_INPUT,
            hover_color="#3a1a1a",
            text_color=ACCENT_STOP,
            border_width=1, border_color=ACCENT_STOP,
            corner_radius=12,
            state="disabled",
            command=self._stop_generation
        )
        self.stop_btn.pack(side="left", padx=(0, 6))

        # Send button
        self.send_btn = ctk.CTkButton(
            btns, text="Send  ↑",
            width=96, height=46,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="white",
            corner_radius=12,
            command=self._on_send
        )
        self.send_btn.pack(side="left")

        ctk.CTkLabel(
            inp_outer,
            text="Enter  to send   •   Shift+Enter  for new line   •   ✏️  to edit any message",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_SECONDARY
        ).pack(pady=(0, 6))

        # Welcome
        self._add_msg(
            "assistant",
            f"Welcome to {APP_NAME}!\n\n"
            "I am your secure, offline laptop assistant.\n\n"
            "🔒  Every action needs your permission\n"
            "📁  Access: Desktop, Downloads, Documents,\n"
            "     Pictures, Music, Videos, D:\\ and E:\\\n"
            "🚫  C:\\ system files are restricted\n"
            "📝  All actions are logged\n\n"
            "⏳  Checking Ollama status...",
            save=False
        )

    # ═══════════════════════════════════════════
    # MESSAGES
    # ═══════════════════════════════════════════

    def _add_msg(self, role, content, save=True, timestamp=""):
        if not timestamp:
            timestamp = time.strftime("%H:%M")
        b = MessageBubble(
            self._msgs_frame, role=role,
            content=content, timestamp=timestamp,
            on_edit=self._on_edit if role == "user" else None
        )
        b.pack(fill="x", pady=2)
        self._msg_widgets.append(b)
        self.after(80, lambda: self._canvas.yview_moveto(1.0))
        if save:
            save_message(role, content)

    def _add_loading(self):
        self._loading_bubble = LoadingBubble(self._msgs_frame)
        self._loading_bubble.pack(fill="x", pady=2)
        self.after(80, lambda: self._canvas.yview_moveto(1.0))

    def _remove_loading(self):
        if self._loading_bubble:
            try:
                self._loading_bubble.stop()
                self._loading_bubble.destroy()
            except:
                pass
            self._loading_bubble = None

    def _load_history_to_chat(self):
        hist = load_history()
        if not hist:
            return
        self._add_msg(
            "assistant",
            f"📂  Loaded {len(hist)} messages from your last session.",
            save=False
        )
        for m in hist[-20:]:
            self._add_msg(
                m["role"], m["content"],
                save=False,
                timestamp=m.get("timestamp", "")[:5]
            )

    # ═══════════════════════════════════════════
    # SEND / STOP / EDIT
    # ═══════════════════════════════════════════

    def _enter_key(self, event):
        if not (event.state & 0x1):
            self._on_send()
            return "break"

    def _on_send(self, event=None):
        if self.locked:
            return
        q = self.input_box.get("1.0", "end").strip()
        if not q:
            return
        if not self.agent:
            self._add_msg(
                "assistant", "⏳  Still loading...", save=False
            )
            return
        self.last_activity = time.time()
        self._add_msg("user", q)
        self.input_box.delete("1.0", "end")
        self._set_ui(thinking=True)
        self._add_loading()
        self._stop_event.clear()
        threading.Thread(
            target=self._response_thread,
            args=(q,), daemon=True
        ).start()

    def _stop_generation(self):
        self._stop_event.set()
        self._remove_loading()
        self._add_msg(
            "assistant", "⏹  Stopped by user.", save=False
        )
        self._set_ui(thinking=False)

    def _on_edit(self, text):
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", text)
        self.input_box.focus()
        self._add_msg(
            "assistant",
            "✏️  Message loaded for editing. Modify and press Send.",
            save=False
        )

    def _response_thread(self, question):
        if self._stop_event.is_set():
            return
        resp = ask_agent(self.agent, question, self._stop_event)
        if not self._stop_event.is_set():
            self.after(0, lambda: self._show_response(resp))

    def _show_response(self, resp):
        self._remove_loading()
        self._add_msg("assistant", resp)
        self._set_ui(thinking=False)

    def _set_ui(self, thinking: bool):
        if thinking:
            self.input_box.configure(state="disabled")
            self.send_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self._set_status("● Thinking...", ORANGE)
        else:
            self.input_box.configure(state="normal")
            self.send_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self._set_status("● Ready", GREEN)

    # ═══════════════════════════════════════════
    # STARTUP
    # ═══════════════════════════════════════════

    def _startup_sequence(self):
        self.after(0, lambda: self._set_status(
            "● Checking Ollama...", ORANGE
        ))
        if not self._ensure_ollama():
            self.after(0, self._on_ollama_failed)
            return
        self.after(0, lambda: self._set_status(
            "● Loading Model...", ORANGE
        ))
        self.after(0, lambda: self._add_msg(
            "assistant",
            f"✅  Ollama running!\n⏳  Loading {OLLAMA_MODEL}...",
            save=False
        ))
        agent, err = load_agent()
        if err:
            self.after(0, lambda: self._on_agent_error(err))
        else:
            self.agent = agent
            self.after(0, self._on_agent_ready)

    def _ensure_ollama(self) -> bool:
        if self._ping():
            self.after(0, lambda: self._add_msg(
                "assistant", "✅  Ollama already running.", save=False
            ))
            return True
        self.after(0, lambda: self._add_msg(
            "assistant",
            "⚙️  Ollama not running — starting automatically...",
            save=False
        ))
        exe = OLLAMA_EXE
        if not os.path.exists(exe):
            for alt in [
                r"C:\Program Files\Ollama\ollama.exe",
                os.path.join(
                    os.environ.get("LOCALAPPDATA", ""),
                    "Programs", "Ollama", "ollama.exe"
                ),
            ]:
                if os.path.exists(alt):
                    exe = alt
                    break
            else:
                return False
        try:
            subprocess.Popen(
                [exe, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            log_error(str(e))
            return False

        for i in range(OLLAMA_WAIT_SECONDS):
            time.sleep(1)
            r = OLLAMA_WAIT_SECONDS - i
            self.after(0, lambda r=r: self._set_status(
                f"● Starting... {r}s", ORANGE
            ))
            if self._ping():
                self.after(0, lambda: self._add_msg(
                    "assistant", "✅  Ollama started!", save=False
                ))
                return True
        return False

    def _ping(self) -> bool:
        try:
            urllib.request.urlopen(OLLAMA_BASE_URL, timeout=2)
            return True
        except:
            return False

    def _on_ollama_failed(self):
        self._set_status("● Ollama Failed", RED)
        self._add_msg(
            "assistant",
            "❌  Could not start Ollama.\n\n"
            "1. Download from https://ollama.com/download\n"
            "2. Open Ollama manually\n"
            "3. Restart Grain Rock",
            save=False
        )

    def _on_agent_ready(self):
        self._set_status("● Ready", GREEN)
        self._add_msg(
            "assistant",
            "✅  Grain Rock is ready!\n\n"
            "Every action will ask for your permission first.\n"
            "Ask me anything about your laptop!",
            save=False
        )

    def _on_agent_error(self, error):
        self._set_status("● Model Error", RED)
        self._add_msg(
            "assistant",
            f"❌  Model failed to load.\n\n"
            f"Run:  ollama pull {OLLAMA_MODEL}\n\n"
            f"Error: {error}",
            save=False
        )

    # ═══════════════════════════════════════════
    # TOOLBAR
    # ═══════════════════════════════════════════

    def _confirm_delete_history(self):
        d = ctk.CTkInputDialog(
            text="Type DELETE to confirm:",
            title="🗑  Delete History"
        )
        if d.get_input() == "DELETE":
            delete_history()
            for w in self._msg_widgets:
                try: w.destroy()
                except: pass
            self._msg_widgets.clear()
            self._add_msg(
                "assistant", "✅  History cleared.", save=False
            )

    def _confirm_delete_memory(self):
        d = ctk.CTkInputDialog(
            text="Type DELETE to confirm:",
            title="🧠 Delete AI Memory"
        )
        if d.get_input() == "DELETE":
            delete_ai_memory()
            self._add_msg(
                "assistant",
                "✅  AI memory cleared completely.",
                save=False
            )

    def _restart_ollama(self):
        self._set_status("● Restarting...", ORANGE)
        self._add_msg(
            "assistant", "🔄  Restarting Ollama...", save=False
        )
        threading.Thread(
            target=self._restart_thread, daemon=True
        ).start()

    def _restart_thread(self):
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "ollama.exe"],
                capture_output=True
            )
            time.sleep(2)
        except: pass
        ok = self._ensure_ollama()
        msg = "✅  Ollama restarted!" if ok else "❌  Restart failed."
        color = GREEN if ok else RED
        self.after(0, lambda: self._set_status("● Ready" if ok else "● Error", color))
        self.after(0, lambda: self._add_msg("assistant", msg, save=False))

    # ═══════════════════════════════════════════
    # SESSION LOCK
    # ═══════════════════════════════════════════

    def _lock_app(self):
        self.locked = True
        self.input_box.configure(state="disabled")
        self.send_btn.configure(state="disabled")
        self._set_status("● Locked 🔒", RED)
        self._add_msg("assistant", "🔒  Session locked.", save=False)
        self._unlock_dialog()

    def _unlock_dialog(self):
        d = ctk.CTkInputDialog(
            text="Type UNLOCK to continue:",
            title="🔒 Locked"
        )
        if d.get_input() == "UNLOCK":
            self.locked = False
            self.input_box.configure(state="normal")
            self.send_btn.configure(state="normal")
            self._set_status("● Ready", GREEN)
            self.last_activity = time.time()
            self._add_msg(
                "assistant", "🔓  Unlocked. Welcome back!", save=False
            )
        else:
            self._unlock_dialog()

    def _start_timeout_checker(self):
        self._check_timeout()

    def _check_timeout(self):
        if not self.locked:
            if time.time() - self.last_activity > SESSION_TIMEOUT * 60:
                self._lock_app()
        self.after(60000, self._check_timeout)

    def _set_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)


if __name__ == "__main__":
    app = GrainRockApp()
    app.mainloop()