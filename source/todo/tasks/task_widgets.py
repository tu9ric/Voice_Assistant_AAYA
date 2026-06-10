import customtkinter as ctk


class SectionTitle(ctk.CTkLabel):

    def __init__(
        self,
        parent,
        text
    ):

        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )


class TagBadge(ctk.CTkLabel):

    def __init__(
        self,
        parent,
        text
    ):

        super().__init__(
            parent,
            text=text,
            height=28,
            corner_radius=14,
            fg_color="#2563EB",
            padx=12
        )


class SecondaryText(ctk.CTkLabel):

    def __init__(
        self,
        parent,
        text
    ):

        super().__init__(
            parent,
            text=text,
            text_color="#9CA3AF"
        )


class Card(ctk.CTkFrame):

    def __init__(
        self,
        parent
    ):

        super().__init__(
            parent,
            corner_radius=22
        )