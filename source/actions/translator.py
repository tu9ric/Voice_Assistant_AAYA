from googletrans import Translator


translator = Translator()

COMMAND_PREFIXES = ("переведи", "перевод")


def _extract_text_to_translate(text: str) -> str:
    lower = text.lower()
    for prefix in COMMAND_PREFIXES:
        if lower.startswith(prefix):
            return text[len(prefix):].strip(" :,-")
    return text


def translate(text: str, dest: str = "en") -> None:
    """Перевод текста (по умолчанию на английский)."""
    phrase = _extract_text_to_translate(text)
    if not phrase:
        print("Нет текста для перевода.")
        return

    try:
        result = translator.translate(phrase, dest=dest)
        print(f"Перевод ({dest}): {result.text}")
    except Exception as e:
        print("Ошибка перевода:", e)
