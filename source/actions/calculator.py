import re
import math

# Словарь русских числительных для конвертации
NUM_WORDS = {
    "ноль": 0, "один": 1, "одна": 1, "первый": 1, "первая": 1,
    "два": 2, "две": 2, "второй": 2, "вторая": 2,
    "три": 3, "третий": 3, "третья": 3,
    "четыре": 4, "четвёртый": 4, "четвертый": 4,
    "пять": 5, "пятый": 5,
    "шесть": 6, "шестой": 6,
    "семь": 7, "седьмой": 7,
    "восемь": 8, "восьмой": 8,
    "девять": 9, "девятый": 9,
    "десять": 10, "десятый": 10,
    "одиннадцать": 11, "двенадцать": 12,
    "тринадцать": 13, "четырнадцать": 14,
    "пятнадцать": 15, "шестнадцать": 16,
    "семнадцать": 17, "восемнадцать": 18,
    "девятнадцать": 19, "двадцать": 20,
}


def convert_word_numbers(text: str) -> str:
    """Преобразует числительные-слова в числа."""
    words = text.split()
    result = []

    for w in words:
        if w in NUM_WORDS:
            result.append(str(NUM_WORDS[w]))
        else:
            result.append(w)

    return " ".join(result)


# Операторы и функции
OPERATIONS = {
    r"\bплюс\b": "+",
    r"\bминус\b": "-",
    r"\bумножить\b": "*",
    r"\bумножь\b": "*",
    r"\bх\b": "*",
    r"\bx\b": "*",
    r"\bразделить\b": "/",
    r"\bделить\b": "/",
    r"\bраздели\b": "/",

    r"\bв\s+степени\b": "**",
    r"\bстепени\b": "**",
    r"\bстепень\b": "**",
}

FUNCTIONS = {
    r"\bкорень\b": "sqrt",
    r"\bсинус\b": "sin",
    r"\bкосинус\b": "cos",
    r"\bтангенс\b": "tan",
    r"\bлогарифм\b": "log",
}


def apply_replacements(text: str, mapping: dict) -> str:
    """Автоматическая регулярная замена по словарю."""
    for pattern, repl in mapping.items():
        text = re.sub(pattern, repl, text)
    return text


def calculate(text: str) -> None:
    """Умный калькулятор с поддержкой словесных команд."""
    text = text.lower()

    # 1) превращаем числительные в цифры
    text = convert_word_numbers(text)

    # 2) заменяем функции и операторы
    text = apply_replacements(text, FUNCTIONS)
    text = apply_replacements(text, OPERATIONS)

    # 3) убираем пробелы
    text = text.replace(" ", "")

    # 4) ищем выражение
    match = re.search(r"[0-9+\-*/()a-zA-Z*]+", text)
    if not match:
        print("Не найдено математическое выражение.")
        return

    expression = match.group(0)

    safe_env = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "sqrt": math.sqrt
    }

    try:
        result = eval(expression, {"__builtins__": None}, safe_env)
        print("Результат:", result)
    except Exception as e:
        print("Ошибка вычисления:", e)
