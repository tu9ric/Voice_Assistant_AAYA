import os
import subprocess
from datetime import datetime

def shutdown(text: str):
    os.system("shutdown /s /t 0")

def restart(text: str):
    os.system("shutdown /r /t 0")

def lock(text: str):
    os.system("rundll32.exe user32.dll,LockWorkStation")

def sleep(text: str):
    # спящий режим
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def tell_time(text: str):
    now = datetime.now().strftime("%H:%M")
    print(f"🕒 Сейчас {now}")

def tell_date(text: str):
    now = datetime.now().strftime("%d.%m.%Y")
    print(f"📅 Сегодня {now}")

def open_notepad(text: str):
    subprocess.Popen("notepad", shell=True)

def open_explorer(text: str):
    subprocess.Popen("explorer", shell=True)

def open_task_manager(text: str):
    subprocess.Popen("taskmgr", shell=True)

def open_settings(text: str):
    subprocess.Popen("start ms-settings:", shell=True)

def open_cmd(text: str):
    subprocess.Popen("start cmd", shell=True)

def open_powershell(text: str):
    subprocess.Popen("start powershell", shell=True)

def open_calculator(text: str):
    subprocess.Popen("calc", shell=True)
