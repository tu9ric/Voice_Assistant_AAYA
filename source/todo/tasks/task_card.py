import customtkinter as ctk

from .task_details import TaskDetailsWindow


class TaskCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        task,
        store,
        on_edit=None,
        on_delete=None,
        on_toggle=None
    ):

        super().__init__(
            parent,
            corner_radius=20
        )

        self.task = task
        self.store = store

        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle = on_toggle

        self.build()

    # =====================================================
    # BUILD
    # =====================================================

    def build(self):

        root = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        root.pack(
            fill="x",
            padx=14,
            pady=14
        )

        # =================================================
        # CHECKBOX DONE
        # =================================================

        self.done_var = ctk.IntVar(
            value=int(
                getattr(
                    self.task,
                    "done",
                    0
                )
            )
        )

        cb = ctk.CTkCheckBox(
            root,
            text="",
            width=28,
            variable=self.done_var,
            command=self.toggle_done
        )

        cb.pack(
            side="left",
            padx=(0, 12)
        )

        # =================================================
        # CONTENT
        # =================================================

        content = ctk.CTkFrame(
            root,
            fg_color="transparent"
        )

        content.pack(
            side="left",
            fill="x",
            expand=True
        )

        title_font = ctk.CTkFont(
            size=18,
            weight="bold"
        )

        if self.done_var.get():

            title_font.configure(
                overstrike=True
            )

        title_btn = ctk.CTkButton(
            content,
            text=self.task.title,
            anchor="w",
            fg_color="transparent",
            hover=False,
            text_color=("black", "white"),
            font=title_font,
            command=self.open_details
        )

        title_btn.pack(
            fill="x"
        )

        # =================================================
        # DATE + TIME
        # =================================================

        dt = self.task.date

        if getattr(
            self.task,
            "time_start",
            None
        ):

            dt += (
                f"  {self.task.time_start}"
            )

            if getattr(
                self.task,
                "time_end",
                None
            ):

                dt += (
                    f" - {self.task.time_end}"
                )

        ctk.CTkLabel(
            content,
            text=dt,
            text_color="#9CA3AF",
            anchor="w"
        ).pack(
            fill="x",
            pady=(2, 0)
        )

        # =================================================
        # TAG
        # =================================================

        if getattr(
            self.task,
            "tag",
            None
        ):

            tag = ctk.CTkLabel(
                content,
                text=self.task.tag,
                height=28,
                corner_radius=14,
                fg_color="#2563EB",
                padx=12
            )

            tag.pack(
                anchor="w",
                pady=(10, 0)
            )

        # =================================================
        # BUTTONS
        # =================================================

        btns = ctk.CTkFrame(
            root,
            fg_color="transparent"
        )

        btns.pack(
            side="right",
            padx=(12, 0)
        )

        ctk.CTkButton(
            btns,
            text="✏",
            width=38,
            command=lambda:
            self.on_edit(self.task)
            if self.on_edit
            else None
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            btns,
            text="🗑",
            width=38,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=lambda:
            self.on_delete(self.task.id)
            if self.on_delete
            else None
        ).pack(
            side="left",
            padx=4
        )

    # =====================================================
    # TOGGLE DONE
    # =====================================================

    def toggle_done(self):

        self.store.update_task_done(
            self.task.id,
            int(
                self.done_var.get()
            )
        )

        if self.on_toggle:

            self.on_toggle()

    # =====================================================
    # OPEN DETAILS
    # =====================================================

    def open_details(self):

        TaskDetailsWindow(
            self.winfo_toplevel(),
            self.task,
            self.store,
            self.on_toggle
        )