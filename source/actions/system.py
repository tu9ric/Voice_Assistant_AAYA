from __future__ import annotations
import os
import platform
import subprocess
from datetime import datetime


def _os() -> str:
    return platform.system().lower()

def restart(text: str):
    os.system("shutdown /r /t 1") 

def lock(text: str):
    print("Невозможно заблокировать экран с помощью ассистента. (пока что)")

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

def open_cmd(text: str):
    """Открыть командную строку (CMD)"""
    try:
        subprocess.Popen("cmd.exe")
        print("Открываю командную строку")
    except Exception as e:
        print(f"Ошибка при открытии CMD: {e}")

def open_powershell(text: str):
    """Открыть PowerShell"""
    try:
        subprocess.Popen("powershell.exe")
        print("Открываю PowerShell")
    except Exception as e:
        print(f"Ошибка при открытии PowerShell: {e}")

def open_settings(text: str):
    """Открыть параметры Windows"""
    try:
        subprocess.Popen("start ms-settings:", shell=True)
        print("Открываю параметры Windows")
    except Exception as e:
        print(f"Ошибка при открытии параметров: {e}")

def open_task_manager(text: str):
    """Открыть диспетчер задач"""
    try:
        os.system("start taskmgr")
        print("Открываю диспетчер задач")
    except Exception as e:
        print(f"Ошибка при открытии диспетчера задач: {e}")


def open_explorer(text: str):
    """Открыть проводник Windows"""
    try:
        subprocess.Popen("explorer.exe")
        print("Открываю проводник")
    except Exception as e:
        print(f"Ошибка при открытии проводника: {e}")


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
