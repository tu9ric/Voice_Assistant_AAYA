import webbrowser


def _open(url: str, description: str) -> None:
    print(f"Открываю {description}…")
    webbrowser.open(url)


def open_youtube(text: str = "") -> None:
    _open("https://youtube.com", "YouTube")


def open_google(text: str = "") -> None:
    _open("https://www.google.com", "Google")


def open_vk(text: str = "") -> None:
    _open("https://vk.com", "ВКонтакте")


def open_yandex(text: str = "") -> None:
    _open("https://yandex.ru", "Яндекс")


def open_github(text: str = "") -> None:
    _open("https://github.com", "GitHub")
