import importlib
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

from utils.text_utils import normalize


FILLER_WORDS = {
    "аая",
    "ая",
    "эй",
    "слушай",
    "пожалуйста",
    "ну",
    "ка",
    "же",
    "мне",
    "давай",
    "можешь",
    "можно",
    "плиз",
    "сейчас",
}


def _smart_normalize(
    text: str
) -> str:

    text = normalize(
        text or ""
    )

    text = text.replace(
        "ё",
        "е"
    )

    text = re.sub(
        r"[^\w\s:+\-*/.,]",
        " ",
        text,
        flags=re.UNICODE
    )

    words = []

    for word in text.split():

        if word not in FILLER_WORDS:

            words.append(
                word
            )

    return " ".join(
        words
    ).strip()


def _similarity(
    a: str,
    b: str
) -> float:

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


def _words_score(
    text: str,
    phrase: str
) -> float:

    text_words = set(
        text.split()
    )

    phrase_words = [
        w
        for w in phrase.split()
        if len(w) > 1
    ]

    if not phrase_words:
        return 0.0

    found = 0

    for word in phrase_words:

        if word in text_words:
            found += 1

    return found / len(
        phrase_words
    )


class CommandProcessor:
    """Гибкий обработчик команд ассистента."""

    def __init__(
        self,
        commands: Dict[str, dict]
    ) -> None:

        self.commands = commands

    def handle(
        self,
        text: str
    ) -> None:

        original_text = text or ""
        normalized_text = _smart_normalize(
            original_text
        )

        if not normalized_text:

            print(
                "Команда пустая."
            )

            return

        match = self._find_best_command(
            normalized_text
        )

        if not match:

            print(
                "Команда не распознана."
            )

            return

        name, info, score = match

        print(
            f"[Команда найдена] {name}"
        )

        self.execute(
            info.get(
                "action",
                ""
            ),
            original_text
        )

    def _find_best_command(
        self,
        text: str
    ):

        best_name = None
        best_info = None
        best_score = 0.0

        for name, info in self.commands.items():

            phrases = info.get(
                "phrases",
                []
            )

            for phrase in phrases:

                phrase_norm = _smart_normalize(
                    str(
                        phrase
                    )
                )

                if not phrase_norm:
                    continue

                score = self._score_phrase(
                    text,
                    phrase_norm
                )

                if score > best_score:

                    best_score = score
                    best_name = name
                    best_info = info

        # Порог специально не слишком высокий:
        # так ассистент понимает разные варианты живой речи.
        if best_score >= 0.62:

            return (
                best_name,
                best_info,
                best_score
            )

        return None

    def _score_phrase(
        self,
        text: str,
        phrase: str
    ) -> float:

        if phrase == text:
            return 1.0

        if phrase in text:
            return 0.95

        if text in phrase:
            return 0.85

        words_score = _words_score(
            text,
            phrase
        )

        sim_score = _similarity(
            text,
            phrase
        )

        return max(
            words_score,
            sim_score
        )

    def execute(
        self,
        action_path: str,
        text: str
    ) -> None:

        if not action_path:

            print(
                "Для этой команды не задано действие."
            )

            return

        try:

            module_name, func_name = action_path.rsplit(
                ".",
                1
            )

            module = importlib.import_module(
                module_name
            )

            func = getattr(
                module,
                func_name
            )

            func(
                text
            )

        except Exception as e:

            print(
                f"Ошибка выполнения действия {action_path}: {e}"
            )