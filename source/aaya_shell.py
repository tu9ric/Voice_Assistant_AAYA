import customtkinter as ctk

from gui import AssistantGUI
from todo.todo_gui import TodoAppGUI
from todo.todo_store import PersonalStore


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AAYAShell(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AAYA Desktop Assistant")
        self.geometry("1500x920")
        self.minsize(1240, 760)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =================================================
        # SIDEBAR
        # =================================================
        self.sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=("#1B1B1D", "#151618")
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns"
        )
        self.sidebar.grid_propagate(False)

        self.sidebar_top = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        self.sidebar_top.pack(
            fill="x",
            padx=24,
            pady=(32, 18)
        )

        self.logo = ctk.CTkLabel(
            self.sidebar_top,
            text="AAYA",
            font=ctk.CTkFont(
                size=34,
                weight="bold"
            )
        )
        self.logo.pack(anchor="w")

        self.logo_sub = ctk.CTkLabel(
            self.sidebar_top,
            text="Desktop Assistant",
            font=ctk.CTkFont(size=14),
            text_color="#9FA4AA"
        )
        self.logo_sub.pack(anchor="w", pady=(2, 0))

        self.nav_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        self.nav_frame.pack(
            fill="x",
            padx=20,
            pady=(10, 0)
        )

        self.voice_btn = ctk.CTkButton(
            self.nav_frame,
            text="🎤 Voice Assistant",
            height=48,
            corner_radius=16,
            anchor="w",
            command=self.show_voice
        )
        self.voice_btn.pack(
            fill="x",
            pady=(0, 10)
        )

        self.todo_btn = ctk.CTkButton(
            self.nav_frame,
            text="📝 TODO",
            height=48,
            corner_radius=16,
            anchor="w",
            command=self.show_todo
        )
        self.todo_btn.pack(
            fill="x",
            pady=(0, 10)
        )

        self.helper_card = ctk.CTkFrame(
            self.sidebar,
            corner_radius=18
        )
        self.helper_card.pack(
            fill="x",
            padx=20,
            pady=(16, 0)
        )

        ctk.CTkLabel(
            self.helper_card,
            text="Подсказка",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=14,
            pady=(14, 4)
        )

        ctk.CTkLabel(
            self.helper_card,
            text="Попробуй сказать:\n"
                 "• открой ютуб\n"
                 "• создай задачу завтра купить продукты\n"
                 "• создай заметку идея проекта",
            justify="left",
            wraplength=190,
            text_color="#B8BDC4",
            font=ctk.CTkFont(size=12)
        ).pack(
            anchor="w",
            padx=14,
            pady=(0, 14)
        )

        self.exit_btn = ctk.CTkButton(
            self.sidebar,
            text="Выход",
            height=46,
            corner_radius=16,
            fg_color="#B00000",
            hover_color="#860000",
            command=self.exit_app
        )
        self.exit_btn.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=22
        )

        # =================================================
        # CONTENT
        # =================================================
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent"
        )
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(0, 0),
            pady=(0, 0)
        )
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Voice frame
        self.voice_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        self.voice_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.voice_gui = AssistantGUI(
            self.voice_frame,
            app_window=self
        )

        # Todo frame
        self.todo_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        try:
            store = PersonalStore()
        except TypeError:
            store = PersonalStore("todo.db")

        self.todo_gui = TodoAppGUI(
            self.todo_frame,
            store
        )

        self.show_voice()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.voice_gui.hide_to_tray
        )

    # =================================================
    # NAV STATE
    # =================================================

    def _set_active_nav(self, active: str):

        default_fg = "#1F6AA5"
        active_fg = "#2E86DE"

        if active == "voice":
            self.voice_btn.configure(fg_color=active_fg)
            self.todo_btn.configure(fg_color=default_fg)
        else:
            self.voice_btn.configure(fg_color=default_fg)
            self.todo_btn.configure(fg_color=active_fg)

    # =================================================
    # SHOW VOICE
    # =================================================

    def show_voice(self):
        self.todo_frame.grid_forget()

        self.voice_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self._set_active_nav("voice")

    # =================================================
    # SHOW TODO
    # =================================================

    def show_todo(self):
        self.voice_frame.grid_forget()

        self.todo_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self._set_active_nav("todo")

    # =================================================
    # EXIT
    # =================================================

    def exit_app(self):
        try:
            self.voice_gui.exit_app()
        except Exception:
            self.destroy()


if __name__ == "__main__":
    app = AAYAShell()
    app.mainloop()