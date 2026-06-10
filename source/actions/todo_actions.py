import re
from datetime import date, datetime, timedelta

from todo.todo_store import PersonalStore


# =====================================================
# HELPERS
# =====================================================

MONTHS = {
    "января": 1,
    "январь": 1,
    "февраля": 2,
    "февраль": 2,
    "марта": 3,
    "март": 3,
    "апреля": 4,
    "апрель": 4,
    "мая": 5,
    "май": 5,
    "июня": 6,
    "июнь": 6,
    "июля": 7,
    "июль": 7,
    "августа": 8,
    "август": 8,
    "сентября": 9,
    "сентябрь": 9,
    "октября": 10,
    "октябрь": 10,
    "ноября": 11,
    "ноябрь": 11,
    "декабря": 12,
    "декабрь": 12,
}


DAY_WORDS = {
    "первого": 1,
    "первое": 1,
    "второго": 2,
    "второе": 2,
    "третьего": 3,
    "третье": 3,
    "четвертого": 4,
    "четвёртого": 4,
    "четвертое": 4,
    "четвёртое": 4,
    "пятого": 5,
    "пятое": 5,
    "шестого": 6,
    "шестое": 6,
    "седьмого": 7,
    "седьмое": 7,
    "восьмого": 8,
    "восьмое": 8,
    "девятого": 9,
    "девятое": 9,
    "десятого": 10,
    "десятое": 10,
    "одиннадцатого": 11,
    "одиннадцатое": 11,
    "двенадцатого": 12,
    "двенадцатое": 12,
    "тринадцатого": 13,
    "тринадцатое": 13,
    "четырнадцатого": 14,
    "четырнадцатое": 14,
    "пятнадцатого": 15,
    "пятнадцатое": 15,
    "шестнадцатого": 16,
    "шестнадцатое": 16,
    "семнадцатого": 17,
    "семнадцатое": 17,
    "восемнадцатого": 18,
    "восемнадцатое": 18,
    "девятнадцатого": 19,
    "девятнадцатое": 19,
    "двадцатого": 20,
    "двадцатое": 20,
    "тридцатого": 30,
    "тридцатое": 30,
    "тридцать первого": 31,
    "тридцать первое": 31,
    "тридцать первого": 31,
}


DAY_WORD_COMBINATIONS = {
    "двадцать первого": 21,
    "двадцать первое": 21,
    "двадцать второго": 22,
    "двадцать второе": 22,
    "двадцать третьего": 23,
    "двадцать третье": 23,
    "двадцать четвертого": 24,
    "двадцать четвёртого": 24,
    "двадцать четвертое": 24,
    "двадцать четвёртое": 24,
    "двадцать пятого": 25,
    "двадцать пятое": 25,
    "двадцать шестого": 26,
    "двадцать шестое": 26,
    "двадцать седьмого": 27,
    "двадцать седьмое": 27,
    "двадцать восьмого": 28,
    "двадцать восьмое": 28,
    "двадцать девятого": 29,
    "двадцать девятое": 29,
    "тридцать первого": 31,
    "тридцать первое": 31,
}


def _today_iso() -> str:

    return date.today().isoformat()


def _nearest_date_by_day(
    day: int
) -> str:

    today = date.today()

    year = today.year
    month = today.month

    try:
        candidate = date(
            year,
            month,
            day
        )

    except Exception:
        candidate = None

    if candidate is None or candidate < today:

        if month == 12:

            month = 1
            year += 1

        else:

            month += 1

        try:
            candidate = date(
                year,
                month,
                day
            )

        except Exception:
            return today.isoformat()

    return candidate.isoformat()


def _find_day_word(
    lowered: str
):

    for phrase, number in DAY_WORD_COMBINATIONS.items():

        if re.search(
            rf"\b{re.escape(phrase)}\b",
            lowered
        ):

            return phrase, number

    for word, number in DAY_WORDS.items():

        if re.search(
            rf"\b{re.escape(word)}\b",
            lowered
        ):

            return word, number

    return None, None


def _parse_date(text: str) -> str:

    lowered = text.lower()
    today = date.today()

    # =====================================================
    # СЛОВЕСНЫЕ ДАТЫ
    # =====================================================

    if "послезавтра" in lowered:

        return (
            today + timedelta(days=2)
        ).isoformat()

    if "завтра" in lowered:

        return (
            today + timedelta(days=1)
        ).isoformat()

    if "сегодня" in lowered:

        return today.isoformat()

    # =====================================================
    # ФОРМАТ: 27 июня / 27 июня 2026
    # =====================================================

    m = re.search(
        r"\b(\d{1,2})\s+("
        r"января|январь|"
        r"февраля|февраль|"
        r"марта|март|"
        r"апреля|апрель|"
        r"мая|май|"
        r"июня|июнь|"
        r"июля|июль|"
        r"августа|август|"
        r"сентября|сентябрь|"
        r"октября|октябрь|"
        r"ноября|ноябрь|"
        r"декабря|декабрь"
        r")(?:\s+(\d{4}))?\b",
        lowered
    )

    if m:

        try:

            day = int(
                m.group(1)
            )

            month = MONTHS[
                m.group(2)
            ]

            year = (
                int(m.group(3))
                if m.group(3)
                else today.year
            )

            return date(
                year,
                month,
                day
            ).isoformat()

        except Exception:
            pass

    # =====================================================
    # ФОРМАТ: тринадцатого июня / двадцать седьмого июня
    # =====================================================

    day_phrase, day_number = _find_day_word(
        lowered
    )

    if day_phrase and day_number:

        month_pattern = (
            r"\b("
            r"января|январь|"
            r"февраля|февраль|"
            r"марта|март|"
            r"апреля|апрель|"
            r"мая|май|"
            r"июня|июнь|"
            r"июля|июль|"
            r"августа|август|"
            r"сентября|сентябрь|"
            r"октября|октябрь|"
            r"ноября|ноябрь|"
            r"декабря|декабрь"
            r")\b"
        )

        month_match = re.search(
            month_pattern,
            lowered
        )

        if month_match:

            try:

                month = MONTHS[
                    month_match.group(1)
                ]

                year_match = re.search(
                    r"\b(20\d{2}|19\d{2})\b",
                    lowered
                )

                year = (
                    int(year_match.group(1))
                    if year_match
                    else today.year
                )

                return date(
                    year,
                    month,
                    day_number
                ).isoformat()

            except Exception:
                pass

        return _nearest_date_by_day(
            day_number
        )

    # =====================================================
    # ФОРМАТ: 2026-05-27
    # =====================================================

    m = re.search(
        r"\b(\d{4})-(\d{2})-(\d{2})\b",
        lowered
    )

    if m:

        try:

            return datetime.strptime(
                m.group(0),
                "%Y-%m-%d"
            ).date().isoformat()

        except Exception:
            pass

    # =====================================================
    # ФОРМАТ: 27.05.2026 / 27-05-2026
    # =====================================================

    m = re.search(
        r"\b(\d{1,2})[.\-](\d{1,2})[.\-](\d{4})\b",
        lowered
    )

    if m:

        try:

            day = int(
                m.group(1)
            )

            month = int(
                m.group(2)
            )

            year = int(
                m.group(3)
            )

            return date(
                year,
                month,
                day
            ).isoformat()

        except Exception:
            pass

    # =====================================================
    # ФОРМАТ: 27.05 / 27-05
    # =====================================================

    m = re.search(
        r"\b(\d{1,2})[.\-](\d{1,2})\b",
        lowered
    )

    if m:

        try:

            day = int(
                m.group(1)
            )

            month = int(
                m.group(2)
            )

            year = today.year

            return date(
                year,
                month,
                day
            ).isoformat()

        except Exception:
            pass

    # =====================================================
    # ФОРМАТ: просто число дня
    # Пример: "создай задачу 27 купить продукты"
    # =====================================================

    m = re.search(
        r"\b(?:на\s+)?(\d{1,2})\b",
        lowered
    )

    if m:

        try:

            day = int(
                m.group(1)
            )

            if 1 <= day <= 31:

                return _nearest_date_by_day(
                    day
                )

        except Exception:
            pass

    return _today_iso()


def _parse_time(text: str):

    lowered = text.lower()

    # =====================================================
    # ФОРМАТ: 15:30
    # =====================================================

    m = re.search(
        r"\b(\d{1,2}):(\d{2})\b",
        lowered
    )

    if m:

        hour = int(
            m.group(1)
        )

        minute = int(
            m.group(2)
        )

        if 0 <= hour <= 23 and 0 <= minute <= 59:

            return f"{hour:02d}:{minute:02d}"

    # =====================================================
    # ФОРМАТ: в 15 часов
    # =====================================================

    m = re.search(
        r"\bв\s+(\d{1,2})\s*(час|часов|часа)?\b",
        lowered
    )

    if m:

        hour = int(
            m.group(1)
        )

        if 0 <= hour <= 23:

            return f"{hour:02d}:00"

    return None


def _remove_day_words(
    text: str
) -> str:

    cleaned = text

    for phrase in DAY_WORD_COMBINATIONS.keys():

        cleaned = re.sub(
            rf"\b{re.escape(phrase)}\b",
            "",
            cleaned
        )

    for word in DAY_WORDS.keys():

        cleaned = re.sub(
            rf"\b{re.escape(word)}\b",
            "",
            cleaned
        )

    return cleaned


def _remove_service_words(text: str) -> str:

    cleaned = text.lower()

    phrases = [
        "создай задачу",
        "добавь задачу",
        "новая задача",
        "запиши задачу",
        "поставь задачу",
        "создать задачу",
        "добавить задачу",
        "создай заметку",
        "добавь заметку",
        "новая заметка",
        "запиши заметку",
        "создать заметку",
        "добавить заметку",
    ]

    for phrase in phrases:

        cleaned = cleaned.replace(
            phrase,
            ""
        )

    cleaned = _remove_day_words(
        cleaned
    )

    service_patterns = [
        r"\bсегодня\b",
        r"\bзавтра\b",
        r"\bпослезавтра\b",

        # 27 июня / 27 июня 2026
        r"\b\d{1,2}\s+(января|январь|февраля|февраль|марта|март|апреля|апрель|мая|май|июня|июнь|июля|июль|августа|август|сентября|сентябрь|октября|октябрь|ноября|ноябрь|декабря|декабрь)(\s+\d{4})?\b",

        # месяц без числа, если число было словом:
        # например "тринадцатого июня купить продукты"
        r"\b(января|январь|февраля|февраль|марта|март|апреля|апрель|мая|май|июня|июнь|июля|июль|августа|август|сентября|сентябрь|октября|октябрь|ноября|ноябрь|декабря|декабрь)\b",

        # 2026-05-27
        r"\b\d{4}-\d{2}-\d{2}\b",

        # 27.05.2026 / 27-05-2026
        r"\b\d{1,2}[.\-]\d{1,2}[.\-]\d{4}\b",

        # 27.05 / 27-05
        r"\b\d{1,2}[.\-]\d{1,2}\b",

        # время
        r"\bв\s+\d{1,2}:\d{2}\b",
        r"\bна\s+\d{1,2}:\d{2}\b",
        r"\bк\s+\d{1,2}:\d{2}\b",
        r"\bв\s+\d{1,2}\s*(час|часов|часа)?\b",

        # просто число даты: "на 27"
        r"\bна\s+\d{1,2}\b",

        # просто число даты: "27"
        r"\b\d{1,2}\b",
    ]

    for pattern in service_patterns:

        cleaned = re.sub(
            pattern,
            "",
            cleaned
        )

    cleaned = cleaned.strip(
        " .,;:-—"
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    )

    return cleaned.strip()


def _get_store() -> PersonalStore:

    return PersonalStore()


def _check_user(store: PersonalStore) -> bool:

    user = store.get_current_user()

    if not user:

        print(
            "Сначала войдите в аккаунт в TODO, потом можно создавать задачи и заметки голосом."
        )

        return False

    return True


# =====================================================
# CREATE TASK
# =====================================================

def create_task(text: str):

    store = _get_store()

    if not _check_user(
        store
    ):

        return

    task_date = _parse_date(
        text
    )

    task_time = _parse_time(
        text
    )

    title = _remove_service_words(
        text
    )

    if not title:

        title = "Новая задача"

    try:

        task = store.create_task(
            title=title,
            date=task_date,
            time_start=task_time,
            time_end=None,
            tag=None,
            description="",
            subtasks_json="[]",
            remind_offsets_json="[]"
        )

        if task_time:

            print(
                f"✅ Задача создана: {task.title}, {task.date} в {task_time}"
            )

        else:

            print(
                f"✅ Задача создана: {task.title}, {task.date}"
            )

    except Exception as e:

        print(
            f"Не удалось создать задачу: {e}"
        )


# =====================================================
# CREATE NOTE
# =====================================================

def create_note(text: str):

    store = _get_store()

    if not _check_user(
        store
    ):

        return

    body = _remove_service_words(
        text
    )

    if not body:

        print(
            "Скажи текст заметки после команды. Например: создай заметку купить продукты."
        )

        return

    title = body[:40]

    if len(body) > 40:

        title += "..."

    try:

        note = store.create_note(
            title=title,
            body=body
        )

        print(
            f"📝 Заметка создана: {note.title}"
        )

    except Exception as e:

        print(
            f"Не удалось создать заметку: {e}"
        )