import customtkinter as ctk
import ctypes

from .todo_store import PersonalStore
from .todo_gui import TodoAppGUI
from .todo_api import TodoAPI

def main():
    # тема (можно менять потом)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Windows AppUserModelID (безопасно только на win)
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AAYA_TODO")
    except Exception:
        pass

    root = ctk.CTk()
    root.title("TODO (AAYA)")
    root.geometry("980x720")
    root.minsize(860, 640)

    store = PersonalStore()
    gui = TodoAppGUI(root, store)

    # локальный API для управления из AAYA
    api = TodoAPI(
        store=store,
        ui_callbacks={
            "show": lambda: root.after(0, gui.ui_show),
            "open_tab": lambda name: root.after(0, lambda: gui.ui_open_tab(name)),
        },
        host="127.0.0.1",
        port=8765
    )
    api.start()

    def on_close():
        # Можно не закрывать процесс, а сворачивать — позже добавим tray
        try:
            api.stop()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()