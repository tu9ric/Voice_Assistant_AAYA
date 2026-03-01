def normalize(text: str) -> str:
    """Нормализует текст: обрезает пробелы и приводит к нижнему регистру."""
    return text.lower().strip()
