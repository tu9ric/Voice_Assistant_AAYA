from __future__ import annotations
import os
import platform
import subprocess
from datetime import datetime


def _os() -> str:
    return platform.system().lower()


def shutdown(text: str):
    if _os() == "windows":
        subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
    elif _os() == "linux":
        subprocess.run(["shutdown", "-h", "now"], check=False)
    else:
        print("ОС не поддерживает shutdown в текущей конфигурации.")


def tell_time(text: str):
    now = datetime.now().strftime("%H:%M")
    print(f"Сейчас {now}")


def tell_date(text: str):
    today = datetime.now().strftime("%d.%m.%Y")
    print(f"Сегодня {today}")


def open_notepad(text: str):
    if _os() == "windows":
        subprocess.run(["notepad.exe"], check=False)
    elif _os() == "linux":
        # пробуем популярные редакторы
        for cmd in (["gedit"], ["kate"], ["nano"], ["xterm", "-e", "nano"]):
            try:
                subprocess.run(cmd, check=False)
                return
            except Exception:
                continue
        print("Не найден текстовый редактор (gedit/kate/nano).")
    else:
        print("ОС не поддерживается.")
