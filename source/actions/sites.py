import webbrowser
import urllib.parse

def open_youtube(text: str):
    webbrowser.open("https://www.youtube.com")

def open_google(text: str):
    webbrowser.open("https://www.google.com")

def open_vk(text: str):
    webbrowser.open("https://vk.com")

def open_yandex(text: str):
    webbrowser.open("https://ya.ru")

def open_github(text: str):
    webbrowser.open("https://github.com")

def open_mail(text: str):
    # откроем универсально (можешь заменить на любимую)
    webbrowser.open("https://mail.google.com")

def open_translate(text: str):
    webbrowser.open("https://translate.google.com")

def open_maps(text: str):
    webbrowser.open("https://www.google.com/maps")

def open_weather(text: str):
    webbrowser.open("https://www.google.com/search?q=weather")

def open_news(text: str):
    webbrowser.open("https://news.google.com")

def open_wikipedia(text: str):
    webbrowser.open("https://ru.wikipedia.org")

def open_twitch(text: str):
    webbrowser.open("https://www.twitch.tv")

def open_reddit(text: str):
    webbrowser.open("https://www.reddit.com")

def _extract_query(text: str, triggers: list[str]) -> str:
    lowered = text.lower()
    for t in triggers:
        if t in lowered:
            idx = lowered.find(t) + len(t)
            return text[idx:].strip(" :,-")
    return ""

def search_google(text: str):
    """Поиск в Google по команде вида 'загугли ...'"""
    try:
        original_text = text.strip()
        lower_text = original_text.lower()

        prefixes = ["загугли", "найди в гугле", "поиск в гугле"]

        query = original_text
        for prefix in prefixes:
            if lower_text.startswith(prefix):
                query = original_text[len(prefix):].strip(" :,-")
                break

        if not query:
            print("Не указан запрос для поиска в Google.")
            return

        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        webbrowser.open(url)
        print(f"Ищу в Google: {query}")

    except Exception as e:
        print(f"Ошибка поиска в Google: {e}")

def search_yandex(text: str):
    """Поиск в Яндексе по команде 'найди ...' / 'заяндексить ...'"""
    try:
        original_text = text.strip()
        lower_text = original_text.lower()

        prefixes = [
            "найди",
            "найди в яндексе",
            "заяндексить",
            "поиск в яндексе"
        ]

        query = original_text

        for prefix in prefixes:
            if lower_text.startswith(prefix):
                query = original_text[len(prefix):].strip(" :,-")
                break

        if not query:
            print("Не указан запрос для поиска в Яндексе.")
            return

        url = "https://yandex.ru/search/?text=" + urllib.parse.quote(query)
        webbrowser.open(url)

        print(f"Ищу в Яндексе: {query}")

    except Exception as e:
        print(f"Ошибка поиска в Яндексе: {e}")