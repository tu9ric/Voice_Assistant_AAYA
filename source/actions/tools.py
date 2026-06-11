import random
import re
import string
import threading
import time
import tkinter as tk


_timer_callback = None


def set_timer_callback(
    callback
):

    global _timer_callback
    _timer_callback = callback


def _timer_finished(
    seconds: int
):

    if _timer_callback:

        try:

            _timer_callback(
                seconds
            )

            return

        except Exception as e:

            print(
                f"Ошибка callback таймера: {e}"
            )

    print(
        "⏰ Таймер! Время вышло."
    )


def roll_dice(
    text: str
):

    n = random.randint(
        1,
        6
    )

    print(
        f"🎲 Выпало: {n}"
    )

    return f"🎲 Выпало: {n}"


def generate_password(
    text: str
):

    m = re.search(
        r"\b(\d{1,2})\b",
        text
    )

    length = int(
        m.group(
            1
        )
    ) if m else 12

    length = max(
        6,
        min(
            length,
            64
        )
    )

    alphabet = string.ascii_letters + string.digits

    pwd = "".join(
        random.choice(
            alphabet
        )
        for _ in range(
            length
        )
    )

    result = f"🔑 Пароль ({length}): {pwd}"

    print(
        result
    )

    return result


def copy_to_clipboard(
    text: str
):

    lowered = text.lower()

    triggers = [
        "скопируй в буфер",
        "в буфер",
        "скопируй текст"
    ]

    payload = text

    for t in triggers:

        if t in lowered:

            idx = lowered.find(
                t
            ) + len(
                t
            )

            payload = text[
                idx:
            ].strip(
                " :,-"
            )

            break

    if not payload:

        result = "Нечего копировать: добавь текст после команды."

        print(
            result
        )

        return result

    r = tk.Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(
        payload
    )
    r.update()
    r.destroy()

    result = "📋 Скопировано в буфер обмена."

    print(
        result
    )

    return result


def _parse_timer_seconds(
    text: str
) -> int:

    lowered = (
        text
        or ""
    ).lower()

    seconds = None

    m = re.search(
        r"(\d+)\s*(сек|секунд|секунда|секунды)",
        lowered
    )

    if m:

        seconds = int(
            m.group(
                1
            )
        )

    m = re.search(
        r"(\d+)\s*(мин|минут|минута|минуты)",
        lowered
    )

    if m:

        seconds = int(
            m.group(
                1
            )
        ) * 60

    m = re.search(
        r"(\d+)\s*(час|часа|часов)",
        lowered
    )

    if m:

        seconds = int(
            m.group(
                1
            )
        ) * 60 * 60

    if seconds is None:

        seconds = 60

    seconds = max(
        1,
        min(
            seconds,
            24 * 60 * 60
        )
    )

    return seconds


def _format_timer_time(
    seconds: int
) -> str:

    if seconds < 60:

        return f"{seconds} сек."

    if seconds < 3600:

        minutes = seconds // 60
        rest = seconds % 60

        if rest:

            return f"{minutes} мин. {rest} сек."

        return f"{minutes} мин."

    hours = seconds // 3600
    minutes = (
        seconds % 3600
    ) // 60

    if minutes:

        return f"{hours} ч. {minutes} мин."

    return f"{hours} ч."


def timer(
    text: str
):

    seconds = _parse_timer_seconds(
        text
    )

    shown_time = _format_timer_time(
        seconds
    )

    result = f"⏱️ Таймер на {shown_time} запущен."

    print(
        result
    )

    def run():

        time.sleep(
            seconds
        )

        _timer_finished(
            seconds
        )

    threading.Thread(
        target=run,
        daemon=True
    ).start()

    return result