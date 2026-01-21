import os
import sys
import json
import threading
from pathlib import Path
from tkinter import Toplevel
import customtkinter as ctk

from core.assistant import Assistant


def resource_path(relative_path: str) -> str:
    base_dir = getattr(sys, "_MEIPASS", None)
    if base_dir:
        return os.path.join(base_dir, relative_path)
    return str(Path(__file__).resolve().parent / relative_path)


class Redirector:
    """Capture prints line-by-line and forward to callback; also mirror to original stdout/stderr."""
    def __init__(self, on_line, mirror_stream):
        self.on_line = on_line
        self.mirror_stream = mirror_stream
        self._buffer = ""

    def write(self, s: str):
        try:
            self.mirror_stream.write(s)
            self.mirror_stream.flush()
        except Exception:
            pass

        self._buffer += s
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if line:
                self.on_line(line)

    def flush(self):
        try:
            self.mirror_stream.flush()
        except Exception:
            pass
        if self._buffer.strip():
            self.on_line(self._buffer.strip())
        self._buffer = ""


class AssistantGUI:
    HOTKEY = "ctrl+shift+space"

    def __init__(self, root):
        self.root = root
        self.root.title("AAYA")
        self.root.geometry("860x680")
        self.root.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # -------- state --------
        self._listening = False
        self._listen_lock = threading.Lock()
        self._last_emitted = None  # dedupe (last answer)

        # -------- notifications (winotify) --------
        self._notify_ok = False
        self._Notification = None
        self._audio = None
        try:
            from winotify import Notification, audio  # type: ignore
            self._Notification = Notification
            self._audio = audio
            self._notify_ok = True
        except Exception:
            self._notify_ok = False

        # -------- toast batching (avoid spam) --------
        self._toast_lock = threading.Lock()
        self._toast_buffer: list[str] = []
        self._toast_timer_active = False

        # -------- hotkey (optional) --------
        self._keyboard = None
        self._hotkey_registered = False
        try:
            import keyboard  # type: ignore
            self._keyboard = keyboard
        except Exception:
            self._keyboard = None

        # -------- UI --------
        header = ctk.CTkFrame(root, height=60, corner_radius=0)
        header.pack(fill="x")
        title = ctk.CTkLabel(header, text="AAYA", font=("Segoe UI", 22))
        title.pack(pady=12)

        self.log_box = ctk.CTkTextbox(
            root,
            width=820,
            height=380,
            corner_radius=12,
            font=("Consolas", 13)
        )
        self.log_box.pack(pady=14)

        self.input_entry = ctk.CTkEntry(
            root,
            width=640,
            height=42,
            placeholder_text="Введите команду и нажмите Enter…",
            font=("Segoe UI", 14)
        )
        self.input_entry.pack(pady=10)
        self.input_entry.bind("<Return>", self.execute_text)
        self.input_entry.focus_set()

        btn_row = ctk.CTkFrame(root)
        btn_row.pack(pady=10)

        self.btn_voice = ctk.CTkButton(
            btn_row,
            text="🎤 Голосовая команда",
            width=200,
            height=42,
            command=self.start_listening
        )
        self.btn_voice.grid(row=0, column=0, padx=10)

        self.btn_text = ctk.CTkButton(
            btn_row,
            text="➡ Выполни текст",
            width=200,
            height=42,
            command=self.execute_text
        )
        self.btn_text.grid(row=0, column=1, padx=10)

        self.btn_commands = ctk.CTkButton(
            btn_row,
            text="📃 Список команд",
            width=200,
            height=42,
            command=self.show_commands_window
        )
        self.btn_commands.grid(row=0, column=2, padx=10)

        self.status = ctk.CTkLabel(
            root,
            text="Статус: ожидание",
            text_color="#4da6ff",
            font=("Segoe UI", 14)
        )
        self.status.pack(pady=10)

        self.theme_switch = ctk.CTkSwitch(root, text="Light / Dark", command=self.toggle_theme)
        self.theme_switch.pack(pady=8)

        # -------- assistant --------
        commands_json = resource_path("commands.json")
        self.assistant = Assistant(commands_json)
        self.processor = self.assistant.processor

        # -------- capture ALL prints --------
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        sys.stdout = Redirector(self._on_any_output_line, self._orig_stdout)
        sys.stderr = Redirector(self._on_any_output_line, self._orig_stderr)

        # Startup info into UI (answers channel, but it's ok)
        self._emit_answer(f"Hotkey: {self.HOTKEY} (если установлен пакет keyboard)")
        self._emit_answer(f"Файл команд: {commands_json}")
        if not self._notify_ok:
            self._emit_answer("Уведомления Windows отключены: установи winotify (pip install winotify)")

        self._setup_hotkey()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- Filtering rules ----------------
    def _is_service_line(self, line: str) -> bool:
        s = line.strip()
        low = s.lower()

        if s.startswith("[") and "]" in s[:80]:
            return True

        service_prefixes = (
            "слушаю",
            "вы сказали",
            "команда:",
            "hotkey:",
            "файл команд:",
            "не понял",
            "не понял речь",
            "ничего не распознано",
            "ничего не распознано.",
        )
        for p in service_prefixes:
            if low.startswith(p):
                return True

        return False

    def _dedupe(self, answer: str) -> bool:
        if not answer:
            return False
        if self._last_emitted == answer:
            return False
        self._last_emitted = answer
        return True

    # ---------------- Output sink (filtered) ----------------
    def _on_any_output_line(self, line: str):
        if self._is_service_line(line):
            return

        answer = line.strip()
        if not self._dedupe(answer):
            return

        self._emit_answer(answer)

    def _emit_answer(self, text: str):
        def _ui():
            self.log_box.insert("end", text + "\n")
            self.log_box.see("end")

        try:
            self.root.after(0, _ui)
        except Exception:
            pass

        self._queue_toast(text)

    # ---------------- Toast ----------------
    def toast_now(self, text: str):
        """Instant toast (used for 'Слушаю…'). Doesn't go into log."""
        if not self._notify_ok:
            return
        self._show_toast("AAYA", text)

    def _queue_toast(self, text: str):
        if not self._notify_ok:
            return

        with self._toast_lock:
            self._toast_buffer.append(text)
            if self._toast_timer_active:
                return
            self._toast_timer_active = True

        def flush():
            with self._toast_lock:
                lines = self._toast_buffer[:]
                self._toast_buffer.clear()
                self._toast_timer_active = False

            if not lines:
                return
            msg = lines[-1]  # latest answer
            self._show_toast("AAYA", msg)

        self.root.after(200, flush)

    def _show_toast(self, title: str, msg: str):
        if not self._notify_ok:
            return

        def _do():
            try:
                n = self._Notification(app_id="AAYA", title=title, msg=msg)
                if self._audio:
                    n.set_audio(self._audio.SMS, loop=False)
                n.show()
            except Exception:
                pass

        try:
            self.root.after(0, _do)
        except Exception:
            pass

    # ---------------- Hotkey ----------------
    def _setup_hotkey(self):
        if not self._keyboard:
            return
        try:
            self._keyboard.add_hotkey(self.HOTKEY, self.start_listening)
            self._hotkey_registered = True
        except Exception:
            self._hotkey_registered = False
            self._emit_answer("Hotkey не включился. Иногда нужен запуск от администратора.")

    # ---------------- Voice flow ----------------
    def start_listening(self):
        if self._listening:
            return
        if not self._listen_lock.acquire(blocking=False):
            return

        self._listening = True
        self.btn_voice.configure(state="disabled")
        self.status.configure(text="Статус: слушаю…", text_color="#00ff99")

        # ✅ Вернули уведомление "Слушаю..." (только toast, без логов)
        self.toast_now("🎤 Слушаю…")

        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        try:
            text = self.assistant.listen()
            if not text:
                return
            self.processor.handle(text)
        finally:
            self.root.after(0, self._finish_listening)

    def _finish_listening(self):
        self.status.configure(text="Статус: ожидание", text_color="#4da6ff")
        self.btn_voice.configure(state="normal")
        self._listening = False
        try:
            self._listen_lock.release()
        except Exception:
            pass

    # ---------------- Text flow ----------------
    def execute_text(self, event=None):
        text = self.input_entry.get().strip()
        if not text:
            return
        try:
            self.processor.handle(text)
        except Exception:
            pass
        self.input_entry.delete(0, "end")
        self.input_entry.focus_set()

    # ---------------- Commands window ----------------
    def show_commands_window(self):
        win = Toplevel(self.root)
        win.title("Список команд")
        win.geometry("760x560")
        win.resizable(False, False)

        txt = ctk.CTkTextbox(win, width=740, height=520, font=("Consolas", 13))
        txt.pack(padx=10, pady=10)

        candidates = [
            resource_path("commands.json"),
            str(Path(__file__).resolve().parent / "commands.json"),
            os.path.join(os.path.abspath("."), "commands.json"),
            os.path.join(os.path.abspath("."), "source", "commands.json"),
        ]

        commands = None
        loaded_from = None
        for p in candidates:
            try:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        commands = json.load(f)
                        loaded_from = p
                        break
            except Exception:
                continue

        if commands is None:
            txt.insert("end", "Не удалось найти commands.json.\n")
            txt.configure(state="disabled")
            return

        txt.insert("end", f"Файл: {loaded_from}\n\n")
        for name, info in commands.items():
            txt.insert("end", f"• {name}\n")
            if isinstance(info, dict):
                phrases = info.get("phrases", [])
                action = info.get("action", "")
                if phrases:
                    txt.insert("end", "    Фразы:\n")
                    for p in phrases:
                        txt.insert("end", f"      - {p}\n")
                if action:
                    txt.insert("end", f"    Действие: {action}\n")
            txt.insert("end", "\n")

        txt.configure(state="disabled")

    # ---------------- Theme ----------------
    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode == "Dark" else "dark")

    # ---------------- Close ----------------
    def on_close(self):
        try:
            if self._keyboard and self._hotkey_registered:
                self._keyboard.unhook_all_hotkeys()
        except Exception:
            pass

        try:
            sys.stdout = self._orig_stdout
            sys.stderr = self._orig_stderr
        except Exception:
            pass

        self.root.destroy()
