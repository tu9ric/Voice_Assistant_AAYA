import importlib
from typing import Dict

from utils.text_utils import normalize, tokenize


class CommandProcessor:
    """Обработчик команд ассистента."""

    def __init__(self, commands: Dict[str, dict]) -> None:
        self.commands = commands

    def _phrase_score(self, user_text: str, phrase: str) -> float:
        user_words = set(tokenize(user_text))
        phrase_words = set(tokenize(phrase))

        if not phrase_words:
            return 0.0

        matched_words = user_words & phrase_words
        return len(matched_words) / len(phrase_words)

    def handle(self, text: str):
        text = normalize(text)

        best_command = None
        best_phrase = None
        best_score = 0.0

        # Если commands.json загружается как словарь
        for command in self.commands.values():
            for phrase in command.get("phrases", []):
                score = self._phrase_score(text, phrase)

                if score > best_score:
                    best_score = score
                    best_command = command
                    best_phrase = phrase

        THRESHOLD = 0.7

        if best_command and best_score >= THRESHOLD:
            action_path = best_command["action"]

            try:
                module_name, func_name = action_path.rsplit(".", 1)
                module = importlib.import_module(module_name)
                func = getattr(module, func_name)

                print(f"Распознана команда: {best_command.get('name', 'unknown')}")
                print(f"Совпавшая фраза: {best_phrase}")
                print(f"Точность совпадения: {best_score:.2f}")

                return func(text)

            except Exception as e:
                print(f"Ошибка при выполнении команды: {e}")
                return

        print("Команда не распознана.")

    def execute(self, action_path: str, text: str) -> None:
        """Выполняет действие по полному пути функции."""
        if not action_path:
            print("Для этой команды не задано действие.")
            return

        try:
            module_name, func_name = action_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
            # Все функции действий принимают один аргумент text (можно игнорировать внутри)
            func(text)
        except Exception as e:
            print(f"Ошибка выполнения действия {action_path}: {e}")
