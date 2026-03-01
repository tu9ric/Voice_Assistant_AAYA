import subprocess

def _run(cmd: str):
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"Не удалось запустить: {cmd}. Ошибка: {e}")

def open_chrome(text: str):
    _run('start "" chrome')

def open_edge(text: str):
    _run('start "" msedge')

def open_telegram(text: str):
    # сначала пытаемся обычный запуск
    _run('start "" Telegram')
    # запасной вариант: открыть web-версию
    _run('start "" https://web.telegram.org/')

def open_discord(text: str):
    _run('start "" Discord')
    _run('start "" https://discord.com/app')

def open_steam(text: str):
    _run('start "" steam')
