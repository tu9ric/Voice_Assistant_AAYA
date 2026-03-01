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
    q = _extract_query(text, ["найди в гугле", "поиск гугл", "загугли"])
    if not q:
        q = "что такое python"
    url = "https://www.google.com/search?q=" + urllib.parse.quote(q)
    webbrowser.open(url)

def search_yandex(text: str):
    q = _extract_query(text, ["найди в яндексе", "поиск яндекс", "заяндекси"])
    if not q:
        q = "что такое python"
    url = "https://yandex.ru/search/?text=" + urllib.parse.quote(q)
    webbrowser.open(url)
