import io
import json
import os
import platform
import subprocess
import sys
import threading
import time
from contextlib import redirect_stdout
from dataclasses import dataclass
from typing import List, Set, Optional

import customtkinter as ctk
from tkinter import messagebox

import speech_recognition as sr

from core.processor import CommandProcessor


HOTKEY = "ctrl+shift+space"

# -------------------------
# Resource path (works in EXE)
# -------------------------
def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# -------------------------
# Platform context
# -------------------------
@dataclass(frozen=True)
class PlatformContext:
    os_name: str
    is_windows: bool
    is_linux: bool
    is_macos: bool


def detect_platform() -> PlatformContext:
    name = platform.system().lower()
    return PlatformContext(
        os_name=name,
        is_windows=(name == "windows"),
        is_linux=(name == "linux"),
        is_macos=(name == "darwin"),
    )


# -------------------------
# Notifier (Windows toast / Linux notify-send / fallback)
# -------------------------
class Notifier:
    def __init__(self, ctx: PlatformContext, app_id: str = "AAYA"):
        self.ctx = ctx
        self.app_id = app_id
        self._win_ok = False
        self._Notification = None
        self._audio = None

        if ctx.is_windows:
            try:
                from winotify import Notification, audio  # type: ignore
                self._Notification = Notification
                self._audio = audio
                self._win_ok = True
            except Exception:
                self._win_ok = False

    def toast(self, title: str, msg: str) -> None:
        msg = (msg or "").strip()
        if not msg:
            return

        if self.ctx.is_windows and self._win_ok:
            try:
                n = self._Notification(app_id=self.app_id, title=title, msg=msg)
                if self._audio:
                    n.set_audio(self._audio.SMS, loop=False)
                n.show()
                return
            except Exception:
                pass

        if self.ctx.is_linux:
            try:
                subprocess.run(
                    ["notify-send", title, msg],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
            except Exception:
                pass

        # fallback
        print(f"{title}: {msg}")


# -------------------------
# Hotkeys wrapper (optional)
# -------------------------
class Hotkeys:
    def __init__(self):
        self._keyboard = None
        try:
            import keyboard  # type: ignore
            self._keyboard = keyboard
        except Exception:
            self._keyboard = None

    @property
    def available(self) -> bool:
        return self._keyboard is not None

    def register(self, hotkey: str, callback) -> bool:
        if not self._keyboard:
            return False
        try:
            self._keyboard.add_hotkey(hotkey, callback)
            return True
        except Exception:
            return False

    def unregister_all(self) -> None:
        if not self._keyboard:
            return
        try:
            self._keyboard.unhook_all_hotkeys()
        except Exception:
            pass


# -------------------------
# Helpers: capture prints & filter for answer/clean lines
# -------------------------
def _clean_output_lines(raw: str) -> List[str]:
    lines = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        low = s.lower()

        # убираем мусорные логи, если где-то остались
        if low.startswith("[") and "]" in low:
            continue

        lines.append(s)
    return lines


def _final_answer_from_captured(raw: str) -> str:
    """
    В тост отправляем только итоговую строку (последнюю осмысленную).
    """
    lines = _clean_output_lines(raw)
    if not lines:
        return ""
    return lines[-1].strip()


# -------------------------
# Tray icon (callbacks -> root.after)
# -------------------------
class Tray:
    def __init__(self, app_name: str, open_cb, exit_cb):
        self.app_name = app_name
        self._open_cb = open_cb
        self._exit_cb = exit_cb
        self._icon = None
        self._thread = None

    def start(self):
        try:
            import pystray
            from PIL import Image, ImageDraw
        except Exception:
            return

        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((8, 8, 56, 56), radius=12, outline=(0, 180, 255, 255), width=4)
        d.text((24, 18), "A", fill=(0, 180, 255, 255))

        menu = pystray.Menu(
            pystray.MenuItem("Открыть", lambda: self._open_cb()),
            pystray.MenuItem("Выход", lambda: self._exit_cb()),
        )

        self._icon = pystray.Icon(self.app_name, img, self.app_name, menu)

        def _run():
            try:
                self._icon.run()
            except Exception:
                pass

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass


# -------------------------
# Commands window
# -------------------------
class CommandsWindow(ctk.CTkToplevel):
    def __init__(self, master, commands_path: str):
        super().__init__(master)
        self.title("Команды")
        self.geometry("750x520")
        self.minsize(650, 450)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(self, text="Список доступных команд",
                             font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, padx=12, pady=(12, 8), sticky="w")

        self.textbox = ctk.CTkTextbox(self, wrap="word")
        self.textbox.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        self._load_commands(commands_path)

    def _load_commands(self, commands_path: str):
        try:
            with open(commands_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            blocks = []
            for cmd_name, info in data.items():
                phrases = info.get("phrases", [])
                action = info.get("action", "")
                blocks.append(f"• {cmd_name}\n  Действие: {action}\n  Фразы: {', '.join(phrases)}\n")

            content = "\n".join(blocks) if blocks else "Команды не найдены."
            self.textbox.insert("1.0", content)
            self.textbox.configure(state="disabled")
        except Exception as e:
            self.textbox.insert("1.0", f"Не удалось загрузить команды: {e}")
            self.textbox.configure(state="disabled")


# -------------------------
# Main GUI (СТАРОЕ ОКНО: большой лог + микрофон + тема + 3 кнопки)
# -------------------------
class AssistantGUI:
    def __init__(self, root):
        self.root = root

        # platform/services
        self.ctx = detect_platform()
        self.notifier = Notifier(self.ctx, app_id="AAYA")
        self.hotkeys = Hotkeys()

        # commands
        self.commands_path = resource_path("commands.json")
        self.commands = self._load_commands(self.commands_path)
        self.processor = CommandProcessor(self.commands)
        self.exit_phrases = self._extract_exit_phrases(self.commands)

        # speech
        self.recognizer = sr.Recognizer()
        self._listen_lock = threading.Lock()
        self._listening = False

        # anti-duplicate recognized text
        self._last_text_handled = ""
        self._last_text_time = 0.0

        # closing flag
        self._closing = False

        # UI
        self._build_ui()

        # tray (safe callbacks)
        self.tray = Tray("AAYA", open_cb=self._tray_open_safe, exit_cb=self._tray_exit_safe)
        self.tray.start()

        # hotkey
        if self.hotkeys.available:
            ok = self.hotkeys.register(HOTKEY, self.start_listening)
            if ok:
                self._log(f"Hotkey: {HOTKEY} (пакет keyboard установлен)")
            else:
                self._log(f"Hotkey: не удалось зарегистрировать {HOTKEY}")
        else:
            self._log("Hotkey: недоступен (установи пакет keyboard)")

        self._log(f"Файл команд: {self.commands_path}")
        self._log(f"ОС: {self.ctx.os_name.capitalize()}")

        # close: hide to tray
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    # ---------- tray-safe ----------
    def _tray_open_safe(self):
        try:
            self.root.after(0, self.show_window)
        except Exception:
            pass

    def _tray_exit_safe(self):
        try:
            self.root.after(0, self.exit_app)
        except Exception:
            pass

    # ---------- UI ----------
    def _build_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        main = ctk.CTkFrame(self.root)
        main.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(main, text="AAYA", font=ctk.CTkFont(size=22, weight="bold"))
        header.grid(row=0, column=0, padx=12, pady=(8, 6), sticky="n")

        # Большой лог
        self.logbox = ctk.CTkTextbox(main, wrap="word")
        self.logbox.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.logbox.configure(state="disabled")

        # Панель ввода
        bottom = ctk.CTkFrame(main)
        bottom.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(bottom, placeholder_text="Введите команду и нажмите Enter…")
        self.entry.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
        self.entry.bind("<Return>", self._on_enter)

        # Кнопки (3 как просил)
        btn_row = ctk.CTkFrame(bottom, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="ew")
        btn_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_voice = ctk.CTkButton(btn_row, text="🎤 Голосовая команда", command=self.start_listening)
        self.btn_voice.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.btn_text = ctk.CTkButton(btn_row, text="➡ Выполни текст", command=self.run_text_command)
        self.btn_text.grid(row=0, column=1, padx=(0, 8), sticky="ew")

        self.btn_cmds = ctk.CTkButton(btn_row, text="📄 Список команд", command=self.open_commands_window)
        self.btn_cmds.grid(row=0, column=2, sticky="ew")

        # Статус + индикатор микрофона + тема
        status_row = ctk.CTkFrame(main, fg_color="transparent")
        status_row.grid(row=3, column=0, padx=12, pady=(0, 6), sticky="ew")
        status_row.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(status_row, text="Статус: ожидание", font=ctk.CTkFont(size=13))
        self.status.grid(row=0, column=0, sticky="w")

        # Индикатор микрофона (справа)
        self.mic_indicator = ctk.CTkLabel(status_row, text="● Микрофон: выкл", font=ctk.CTkFont(size=13))
        self.mic_indicator.grid(row=0, column=1, sticky="e")

        # Переключатель темы
        self.theme_switch = ctk.CTkSwitch(main, text="Light / Dark", command=self.toggle_theme)
        self.theme_switch.grid(row=4, column=0, padx=12, pady=(0, 2), sticky="s")

        # По умолчанию в main.py выставлена dark, синхронизируем свитч:
        # (если сейчас dark -> переключатель "включен")
        try:
            current = ctk.get_appearance_mode()
            self.theme_switch.select() if current.lower() == "dark" else self.theme_switch.deselect()
        except Exception:
            self.theme_switch.select()

    # ---------- logging ----------
    def _log(self, text: str):
        if not text:
            return
        self.logbox.configure(state="normal")
        self.logbox.insert("end", text.strip() + "\n")
        self.logbox.see("end")
        self.logbox.configure(state="disabled")

    def set_status(self, text: str):
        self.status.configure(text=text)

    def set_mic(self, on: bool):
        if on:
            self.mic_indicator.configure(text="● Микрофон: ВКЛ")
        else:
            self.mic_indicator.configure(text="● Микрофон: выкл")

    # ---------- theme ----------
    def toggle_theme(self):
        # switch ON -> dark, OFF -> light
        try:
            if self.theme_switch.get() == 1:
                ctk.set_appearance_mode("dark")
                self._log("Тема: Dark")
            else:
                ctk.set_appearance_mode("light")
                self._log("Тема: Light")
        except Exception:
            pass

    # ---------- events ----------
    def _on_enter(self, event=None):
        self.run_text_command()
        return "break"

    def open_commands_window(self):
        win = CommandsWindow(self.root, self.commands_path)
        win.focus()

    # ---------- load commands ----------
    def _load_commands(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("AAYA", f"Не удалось загрузить commands.json:\n{e}")
            return {}

    def _extract_exit_phrases(self, commands: dict) -> Set[str]:
        default = {"пока", "до свидания", "выключись", "закройся", "bye"}
        try:
            bye = commands.get("bye", {})
            phrases = bye.get("phrases", [])
            s = {str(p).strip().lower() for p in phrases if str(p).strip()}
            return s or default
        except Exception:
            return default

    # ---------- text command ----------
    def run_text_command(self):
        text = (self.entry.get() or "").strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._handle_text(text)

    def _handle_text(self, text: str):
        norm = text.strip().lower()
        now = time.time()

        # антидубль
        if norm and norm == self._last_text_handled and (now - self._last_text_time) < 1.2:
            return
        self._last_text_handled = norm
        self._last_text_time = now

        if norm in self.exit_phrases:
            self._log("Команда: пока -> завершение работы")
            self.notifier.toast("AAYA", "Выключаюсь.")
            self.exit_app()
            return

        self.set_status("Статус: выполняю команду")
        self._log(f"Команда: {text}")

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.processor.handle(norm)

        raw = buf.getvalue()
        cleaned = _clean_output_lines(raw)

        # Всё, что напечатали actions — добавляем в лог (как тебе нужно)
        for line in cleaned:
            self._log(line)

        # В тост — только итоговый ответ (последняя строка)
        answer = _final_answer_from_captured(raw) or "Готово."
        self.notifier.toast("AAYA", answer)

        self.set_status("Статус: ожидание")

    # ---------- voice ----------
    def start_listening(self):
        if self._listening:
            return
        if not self._listen_lock.acquire(blocking=False):
            return

        self._listening = True
        self.root.after(0, lambda: self.set_mic(True))
        self.root.after(0, lambda: self.set_status("Статус: слушаю"))
        self.root.after(0, lambda: self._log("Слушаю…"))
        self.notifier.toast("AAYA", "🎤 Слушаю…")

        t = threading.Thread(target=self._listen_thread, daemon=True)
        t.start()

    def _listen_thread(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source)

            try:
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                text = (text or "").strip()
            except sr.UnknownValueError:
                text = ""
            except sr.RequestError:
                text = ""
                self.notifier.toast("AAYA", "Ошибка сервиса распознавания речи.")
                self.root.after(0, lambda: self._log("Ошибка: сервис распознавания речи недоступен"))
            except Exception:
                text = ""

            if text:
                self.root.after(0, lambda t=text: self._log(f"Распознано: {t}"))
                self.root.after(0, lambda t=text: self._handle_text(t))
            else:
                self.root.after(0, lambda: self._log("Ничего не распознано."))

        except Exception:
            self.notifier.toast("AAYA", "Ошибка микрофона или доступа к аудио.")
            self.root.after(0, lambda: self._log("Ошибка: микрофон или доступ к аудио"))
        finally:
            self._listening = False
            try:
                self._listen_lock.release()
            except Exception:
                pass
            self.root.after(0, lambda: self.set_mic(False))
            self.root.after(0, lambda: self.set_status("Статус: ожидание"))

    # ---------- tray behavior ----------
    def hide_to_tray(self):
        # Прячем окно, приложение остаётся работать
        try:
            self.root.after_idle(self.root.withdraw)
        except Exception:
            pass
        self.notifier.toast("AAYA", "Работает в фоне. Открыть можно из трея.")
        self._log("Окно скрыто в трей (приложение работает в фоне).")

    def show_window(self):
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass

    def exit_app(self):
        if self._closing:
            return
        self._closing = True

        self._log("Завершение работы…")

        try:
            self.hotkeys.unregister_all()
        except Exception:
            pass

        try:
            self.tray.stop()
        except Exception:
            pass

        try:
            self.root.destroy()
        except Exception:
            pass

        os._exit(0)
