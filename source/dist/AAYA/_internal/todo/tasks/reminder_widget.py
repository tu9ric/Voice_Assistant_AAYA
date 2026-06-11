import customtkinter as ctk


REMINDER_PRESETS = [
    ("Нет", ""),
    ("За 5 минут", "PT5M"),
    ("За 15 минут", "PT15M"),
    ("За 30 минут", "PT30M"),
    ("За 1 час", "PT1H"),
    ("За 3 часа", "PT3H"),
    ("За 1 день", "P1D"),
]


class ReminderWidget(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        selected=None
    ):

        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.selected = selected or ""

        self.build()

    # =====================================================
    # BUILD
    # =====================================================

    def build(self):

        ctk.CTkLabel(
            self,
            text="Напоминание",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.menu = ctk.CTkOptionMenu(
            self,
            values=[
                x[0]
                for x in REMINDER_PRESETS
            ]
        )

        self.menu.pack(
            fill="x"
        )

        current_name = "Нет"

        for name, code in REMINDER_PRESETS:

            if code == self.selected:
                current_name = name
                break

        self.menu.set(current_name)

    # =====================================================
    # GET VALUE
    # =====================================================

    def get_value(self):

        current = self.menu.get()

        for name, code in REMINDER_PRESETS:

            if name == current:
                return code

        return ""