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
    def __init__(self):
        super().__init__()

        self.title("AAYA Desktop Assistant")
        self.geometry("1450x900")
        self.minsize(1200, 700)

        # layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =========================
        # SIDEBAR
        # =========================
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.sidebar.grid_rowconfigure(10, weight=1)

        # logo
        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="AAYA",
            font=("Segoe UI", 34, "bold")
        )
        self.logo.pack(pady=(40, 30))

        # voice button
        self.voice_btn = ctk.CTkButton(
            self.sidebar,
            text="🎤 Voice Assistant",
            height=50,
            command=self.show_voice
        )
        self.voice_btn.pack(fill="x", padx=20, pady=10)

        # todo button
        self.todo_btn = ctk.CTkButton(
            self.sidebar,
            text="📝 TODO",
            height=50,
            command=self.show_todo
        )
        self.todo_btn.pack(fill="x", padx=20, pady=10)

        # exit
        self.exit_btn = ctk.CTkButton(
            self.sidebar,
            text="Выход",
            fg_color="#8B0000",
            hover_color="#5E0000",
            command=self.destroy
        )
        self.exit_btn.pack(side="bottom", fill="x", padx=20, pady=20)

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
        self.voice_frame = ctk.CTkFrame(self.content)
        self.voice_frame.pack(fill="both", expand=True)

        self.voice_gui = AssistantGUI(self.voice_frame)

        # =========================
        # TODO FRAME
        # =========================
        self.todo_frame = ctk.CTkFrame(self.content)

        try:
            store = PersonalStore()
        except TypeError:
            store = PersonalStore("todo.db")

        self.todo_gui = TodoAppGUI(self.todo_frame, store)

        # скрываем TODO при старте
        self.todo_frame.pack_forget()

    # =========================
    # SHOW VOICE
    # =========================
    def show_voice(self):
        self.todo_frame.pack_forget()
        self.voice_frame.pack(fill="both", expand=True)

    # =========================
    # SHOW TODO
    # =========================
    def show_todo(self):
        self.voice_frame.pack_forget()
        self.todo_frame.pack(fill="both", expand=True)


# =========================
# START APP
# =========================
if __name__ == "__main__":
    app = AAYAShell()
    app.mainloop()