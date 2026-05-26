from datetime import date as ddate

RU_WEEKDAY_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

RU_MONTHS = [
    "Январь", "Февраль", "Март", "Апрель",
    "Май", "Июнь", "Июль", "Август",
    "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]


def parse_hm(s: str) -> tuple[int, int]:
    h, m = s.split(":")
    return int(h), int(m)


def minutes(hm: str) -> int:
    h, m = parse_hm(hm)
    return h * 60 + m


def ui_date(d: ddate) -> str:
    return d.strftime("%d-%m-%Y")