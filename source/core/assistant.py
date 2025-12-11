import json
from typing import Dict

import speech_recognition as sr

from core.processor import CommandProcessor

import sys, os

def resource_path(relative_path):
    """Работает и в Python, и в EXE"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class Assistant:
    """Голосовой ассистент."""

    def __init__(self, commands_path: str) -> None:
        json_path = resource_path(commands_path)
        self.commands: Dict[str, dict] = self._load_commands(json_path)
        self.processor = CommandProcessor(self.commands)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    @staticmethod
    def _load_commands(path: str) -> Dict[str, dict]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def listen(self) -> str:
        """Распознаёт речь с микрофона и возвращает текст."""
        with self.microphone as source:
            print("Слушаю…")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            print(f"Вы сказали: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Не понял речь.")
        except sr.RequestError:
            print("Ошибка сервиса распознавания речи.")

        return ""

    def run(self) -> None:
        """Основной цикл ассистента."""
        print('Голосовой ассистент запущен. Скажите команду (или скажите "выход" для завершения).')
        while True:
            text = self.listen()
            if not text:
                continue

            if text in ("выход", "quit", "exit", "стоп"):
                print("Завершение работы ассистента.")
                break

            self.processor.handle(text)
