import random
import re


JOKES = [
    "Программист — это машина, превращающая кофе в код.",
    "Почему программисты путают Хэллоуин и Рождество? Потому что OCT 31 == DEC 25.",
    "Сначала не понял рекурсию… Потом понял рекурсию.",
    "Работает? Не трогай!"
]


def tell_joke(text: str = "") -> None:
    """Рассказывает случайную шутку."""
    print("Шутка:", random.choice(JOKES))


def flip_coin(text: str = "") -> None:
    """Подбрасывает монетку."""
    result = random.choice(["орёл", "решка"])
    print(f"Монетка: {result}.")


def random_number(text: str = "") -> None:
    """Выдаёт случайное число. Если в тексте есть границы — использует их."""
    match = re.search(r"(\d+)\D+(\d+)", text)
    if match:
        a, b = sorted(map(int, match.groups()))
    else:
        a, b = 1, 100

    value = random.randint(a, b)
    print(f"Случайное число от {a} до {b}: {value}")


