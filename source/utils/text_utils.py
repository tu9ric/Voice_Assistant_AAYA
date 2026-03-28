import re
import pymorphy3

morph = pymorphy3.MorphAnalyzer()


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list[str]:
    words = normalize(text).split()
    result = []

    for word in words:
        parsed = morph.parse(word)[0]
        result.append(parsed.normal_form)

    return result