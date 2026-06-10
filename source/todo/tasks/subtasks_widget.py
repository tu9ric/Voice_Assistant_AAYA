import customtkinter as ctk


class SubtasksWidget(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        subtasks=None
    ):

        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.items = []

        self.container = ctk.CTkFrame(
            self,
            corner_radius=18
        )

        self.container.pack(
            fill="x",
            pady=(0, 10)
        )

        if subtasks:

            for sub in subtasks:

                self.add_subtask(
                    sub.get("text", ""),
                    sub.get("done", 0)
                )

        btn = ctk.CTkButton(
            self,
            text="➕ Добавить подзадачу",
            command=lambda:
            self.add_subtask("")
        )

        btn.pack(fill="x")

    def add_subtask(
        self,
        text="",
        done=0
    ):

        row = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=10,
            pady=6
        )

        var = ctk.IntVar(
            value=int(done)
        )

        cb = ctk.CTkCheckBox(
            row,
            text="",
            variable=var,
            width=24
        )

        cb.pack(
            side="left",
            padx=(0, 8)
        )

        entry = ctk.CTkEntry(
            row,
            placeholder_text="Подзадача"
        )

        entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        if text:
            entry.insert(0, text)

        self.items.append(
            (var, entry)
        )

    def get_data(self):

        result = []

        for var, entry in self.items:

            txt = (
                entry.get() or ""
            ).strip()

            if not txt:
                continue

            result.append({
                "text": txt,
                "done": int(var.get())
            })

        return result