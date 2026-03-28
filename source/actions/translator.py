from googletrans import Translator
import re


translator = Translator()

COMMAND_PREFIXES = ("переведи", "перевод")


def _extract_text_to_translate(text: str) -> str:
    lower = text.lower()
    for prefix in COMMAND_PREFIXES:
        if lower.startswith(prefix):
            return text[len(prefix):].strip(" :,-")
    return text.strip()


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _contains_cyrillic(text: str) -> bool:
    return bool(re.search(r"[а-яё]", text.lower()))


def _contains_latin(text: str) -> bool:
    return bool(re.search(r"[a-z]", text.lower()))


def _is_bad_translation(source: str, translated: str) -> bool:
    """
    Определяет:
    - перевод совпадает с исходным
    - или это просто транслит
    """

    src = _normalize(source)
    tr = _normalize(translated)

    if not src or not tr:
        return True

    # Полное совпадение
    if src == tr:
        return True

    # Похожесть строк (транслит/мусор)
    same = sum(1 for a, b in zip(src, tr) if a == b)
    similarity = same / max(len(src), len(tr))

    if similarity > 0.7:
        return True

    # Кириллица → латиница (часто транслит)
    if _contains_cyrillic(src) and _contains_latin(tr):
        if abs(len(src) - len(tr)) <= 2:
            return True

    return False


def translate(text: str, dest: str = "en") -> None:
    """Перевод текста (по умолчанию на английский)."""

    phrase = _extract_text_to_translate(text)

    if not phrase:
        print("Нет текста для перевода.")
        return

    try:
        result = translator.translate(phrase, dest=dest)
        translated = result.text.strip()

        # 🔥 проверка "нормальности" перевода
        if _is_bad_translation(phrase, translated):
            print(f"Не знаю, как перевести: {phrase}")
            return

        print(f"Перевод ({dest}): {translated}")

    except Exception as e:
        print("Ошибка перевода:", e)