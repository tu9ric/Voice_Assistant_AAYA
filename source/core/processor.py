import importlib
from typing import Dict

from utils.text_utils import normalize


class CommandProcessor:
    """Обработчик команд ассистента."""

    def __init__(self, commands: Dict[str, dict]) -> None:
        self.commands = commands

    def handle(self, text: str) -> None:
        """Подбирает команду по тексту и выполняет её."""
        text = normalize(text)

        for name, info in self.commands.items():
            for phrase in info.get("phrases", []):
                if phrase in text:
                    print(f"[Команда найдена] {name}")
                    self.execute(info.get("action", ""), text)
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
