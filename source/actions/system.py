import os
import platform
import subprocess
from datetime import datetime


def shutdown(text: str = "") -> None:
    """Выключение компьютера (только для Windows)."""
    print("Выключение компьютера…")
    if platform.system().lower() == "windows":
        os.system("shutdown /s /t 0")
    else:
        print("Автовыключение поддерживается только в Windows.")


def tell_time(text: str = "") -> None:
    """Сообщает текущее время."""
    now = datetime.now().strftime("%H:%M")
    print(f"Сейчас {now}.")


def tell_date(text: str = "") -> None:
    """Сообщает текущую дату."""
    today = datetime.now().strftime("%d.%m.%Y")
    print(f"Сегодня {today}.")


def open_notepad(text: str = "") -> None:
    """Открывает блокнот (Windows)."""
    print("Открываю блокнот…")
    if platform.system().lower() == "windows":
        try:
            subprocess.Popen(["notepad.exe"])
        except FileNotFoundError:
            print("Не удалось найти notepad.exe")
    else:
        print("Открытие блокнота реализовано только для Windows.")
