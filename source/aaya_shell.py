import customtkinter as ctk

from gui import AssistantGUI

from todo.todo_gui import TodoAppGUI
from todo.todo_store import PersonalStore


# =========================
# CONFIG
# =========================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================
# MAIN SHELL
# =========================

class AAYAShell(ctk.CTk):

    def __init__(
        self
    ):

        super().__init__()

        self.title(
            "AAYA Desktop Assistant"
        )

        self.geometry(
            "1450x900"
        )

        self.minsize(
            1200,
            700
        )

        # layout
        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        # =========================
        # SIDEBAR
        # =========================

        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        self.sidebar.grid_rowconfigure(
            10,
            weight=1
        )

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="AAYA",
            font=(
                "Segoe UI",
                34,
                "bold"
            )
        )

        self.logo.pack(
            pady=(40, 30)
        )

        self.voice_btn = ctk.CTkButton(
            self.sidebar,
            text="🎤 Voice Assistant",
            height=50,
            command=self.show_voice
        )

        self.voice_btn.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.todo_btn = ctk.CTkButton(
            self.sidebar,
            text="📝 TODO",
            height=50,
            command=self.show_todo
        )

        self.todo_btn.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.exit_btn = ctk.CTkButton(
            self.sidebar,
            text="Выход",
            fg_color="#8B0000",
            hover_color="#5E0000",
            command=self.exit_app
        )

        self.exit_btn.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=20
        )

        # =========================
        # CONTENT
        # =========================

        self.content = ctk.CTkFrame(
            self,
            corner_radius=0
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        # =========================
        # VOICE FRAME
        # =========================

        self.voice_frame = ctk.CTkFrame(
            self.content
        )

        self.voice_frame.pack(
            fill="both",
            expand=True
        )

        # ВАЖНО:
        # AssistantGUI рисуется внутри voice_frame,
        # но управляет главным окном self.
        self.voice_gui = AssistantGUI(
            self.voice_frame,
            app_window=self
        )

        # =========================
        # TODO FRAME
        # =========================

        self.todo_frame = ctk.CTkFrame(
            self.content
        )

        try:

            store = PersonalStore()

        except TypeError:

            store = PersonalStore(
                "todo.db"
            )

        self.todo_gui = TodoAppGUI(
            self.todo_frame,
            store
        )

        self.todo_frame.pack_forget()

        # Главное закрытие окна теперь уходит в фон,
        # а не убивает приложение.
        self.protocol(
            "WM_DELETE_WINDOW",
            self.voice_gui.hide_to_tray
        )

    # =========================
    # SHOW VOICE
    # =========================

    def show_voice(
        self
    ):

        self.todo_frame.pack_forget()

        self.voice_frame.pack(
            fill="both",
            expand=True
        )

    # =========================
    # SHOW TODO
    # =========================

    def show_todo(
        self
    ):

        self.voice_frame.pack_forget()

        self.todo_frame.pack(
            fill="both",
            expand=True
        )

    # =========================
    # EXIT
    # =========================

    def exit_app(
        self
    ):

        try:
            self.voice_gui.exit_app()

        except Exception:

            self.destroy()


# =========================
# START APP
# =========================

if __name__ == "__main__":

    app = AAYAShell()
    app.mainloop()