from datetime import datetime


HOURS = [f"{h:02d}" for h in range(24)]

MINUTES = ["00", "15", "30", "45"]


REMINDER_PRESETS = [
    ("Нет", ""),
    ("За 5 минут", "PT5M"),
    ("За 15 минут", "PT15M"),
    ("За 30 минут", "PT30M"),
    ("За 1 час", "PT1H"),
    ("За 3 часа", "PT3H"),
    ("За 1 день", "P1D"),
]


def hm(h, m):

    return f"{h}:{m}"


def parse_hm(s):

    h, m = s.split(":")

    return int(h), int(m)


def minutes(hm_value):

    h, m = parse_hm(hm_value)

    return h * 60 + m


def ui_date(date_str):

    try:

        return datetime.strptime(
            date_str,
            "%Y-%m-%d"
        ).strftime("%d-%m-%Y")

    except Exception:

        return date_str