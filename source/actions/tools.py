import random
import re
import string
import threading
import time
import tkinter as tk

def roll_dice(text: str):
    n = random.randint(1, 6)
    print(f"🎲 Выпало: {n}")

def generate_password(text: str):
    m = re.search(r"\b(\d{1,2})\b", text)
    length = int(m.group(1)) if m else 12
    length = max(6, min(length, 64))

    alphabet = string.ascii_letters + string.digits
    pwd = "".join(random.choice(alphabet) for _ in range(length))
    print(f"🔑 Пароль ({length}): {pwd}")
    return pwd

def copy_to_clipboard(text: str):
    lowered = text.lower()
    triggers = ["скопируй в буфер", "в буфер", "скопируй текст"]
    payload = text
    for t in triggers:
        if t in lowered:
            idx = lowered.find(t) + len(t)
            payload = text[idx:].strip(" :,-")
            break

    if not payload:
        print("Нечего копировать: добавь текст после команды.")
        return

    r = tk.Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(payload)
    r.update()
    r.destroy()
    print("📋 Скопировано в буфер обмена.")

def timer(text: str):
    lowered = text.lower()
    seconds = None

    m = re.search(r"(\d+)\s*(сек|секунд)", lowered)
    if m:
        seconds = int(m.group(1))

    m = re.search(r"(\d+)\s*(мин|минут)", lowered)
    if m:
        seconds = int(m.group(1)) * 60

    if seconds is None:
        seconds = 60

    seconds = max(1, min(seconds, 24 * 60 * 60))
    print(f"⏱️ Таймер на {seconds} сек запущен.")

    def run():
        time.sleep(seconds)
        print("⏰ Таймер! Время вышло.")

    threading.Thread(target=run, daemon=True).start()
