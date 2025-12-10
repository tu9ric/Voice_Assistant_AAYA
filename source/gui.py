import threading
import customtkinter as ctk
from tkinter import Toplevel
import json
import sys

from core.assistant import Assistant
from core.processor import CommandProcessor


# ----------------------- Перехват print -----------------------
class Redirector:
    """Позволяет выводить print() прямо в текстовое поле GUI."""
    def __init__(self, write_func):
        self.write_func = write_func

    def write(self, text):
        if text.strip():
            self.write_func(text)

    def flush(self):
        pass


# ----------------------- GUI Ассистента -----------------------
class AssistantGUI:
    def __init__(self, root):
        self.root = root

        # Заголовок окна
        self.root.title("Голосовой ассистент AAYA")
        self.root.resizable(False, False)

        # Главный фон для исправления тёмной темы
        bg = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        self.root.configure(fg_color=bg)

        # ---------- Инициализация ассистента ----------
        self.assistant = Assistant("commands.json")
        self.processor = self.assistant.processor

        # ---------- Верхняя панель ----------
        header = ctk.CTkFrame(root, height=60, corner_radius=0)
        header.pack(fill="x")

        title = ctk.CTkLabel(
            header, text="Голосовой ассистент AAYA",
            font=("Segoe UI", 20)
        )
        title.pack(pady=10)

        # ---------- Лог ----------
        self.log = ctk.CTkTextbox(
            root, width=780, height=360,
            corner_radius=10, font=("Consolas", 14)
        )
        self.log.pack(pady=15)

        # Перенаправляем print в лог GUI
        sys.stdout = Redirector(self.log_message)
        sys.stderr = Redirector(self.log_message)

        # ---------- Поле ввода ----------
        self.input_entry = ctk.CTkEntry(
            root, width=600, height=40,
            placeholder_text="Введите команду...",
            font=("Segoe UI", 14)
        )
        self.input_entry.pack(pady=10)

        # ---------- Кнопки ----------
        button_frame = ctk.CTkFrame(root)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="🎤 Голосовая команда",
                      width=180, height=40,
                      command=self.start_listening).grid(row=0, column=0, padx=10)

        ctk.CTkButton(button_frame, text="➡ Выполнить текст",
                      width=180, height=40,
                      command=self.execute_text).grid(row=0, column=1, padx=10)

        ctk.CTkButton(button_frame, text="📃 Список команд",
                      width=180, height=40,
                      command=self.show_commands_window).grid(row=0, column=2, padx=10)

        # ---------- Статус ----------
        self.status = ctk.CTkLabel(
            root, text="Статус: ожидание",
            text_color="#4da6ff", font=("Segoe UI", 14)
        )
        self.status.pack(pady=10)

        # ---------- Переключатель темы ----------
        self.theme_switch = ctk.CTkSwitch(
            root, text="Переключить тему (Dark / Light)",
            command=self.toggle_theme
        )
        self.theme_switch.pack(pady=10)

    # ----------------------- Логирование -----------------------
    def log_message(self, message):
        self.log.insert("end", message + "\n")
        self.log.see("end")

    # ----------------------- Голосовая команда -----------------------
    def start_listening(self):
        threading.Thread(target=self.listen_thread, daemon=True).start()

    def listen_thread(self):
        self.status.configure(text="Статус: слушаю...", text_color="#00ff99")
        text = self.assistant.listen()
        self.status.configure(text="Статус: ожидание", text_color="#4da6ff")

        if text:
            print(f"Вы сказали: {text}")
            self.processor.handle(text)

    # ----------------------- Ввод текста -----------------------
    def execute_text(self):
        text = self.input_entry.get().strip()
        if not text:
            return
        print(f"Текстовая команда: {text}")
        self.processor.handle(text)

    # ----------------------- Список команд -----------------------
    def show_commands_window(self):
        try:
            with open("commands.json", "r", encoding="utf-8") as f:
                commands = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки commands.json: {e}")
            return

        win = ctk.CTkToplevel(self.root)
        win.title("Список доступных команд")
        win.geometry("600x500")

        txt = ctk.CTkTextbox(win, width=560, height=440, corner_radius=10)
        txt.pack(pady=10)

        for name, info in commands.items():
            txt.insert("end", f"Команда: {name}\n")
            txt.insert("end", "  Фразы:\n")
            for p in info.get("phrases", []):
                txt.insert("end", f"    — {p}\n")
            txt.insert("end", f"  Действие: {info['action']}\n\n")

        txt.configure(state="disabled")

    # ----------------------- Переключение темы -----------------------
    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode == "Dark" else "dark")

        # Исправление фона окна
        bg = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        self.root.configure(fg_color=bg)
