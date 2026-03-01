from win10toast import ToastNotifier

_toaster = ToastNotifier()

def show_listening():
    _toaster.show_toast(
        "Голосовой ассистент",
        "🎤 Слушаю...",
        duration=2,
        threaded=True
    )
