import customtkinter as ctk
import json


class TaskDetailsWindow:

    def __init__(
        self,
        parent,
        task,
        store
    ):

        self.parent = parent
        self.task = task
        self.store = store

        self.build()

    def build(self):

        self.win = ctk.CTkToplevel(
            self.parent
        )

        self.win.title(
            self.task.title
        )

        self.win.geometry(
            "560x720"
        )

        self.win.lift()

        self.win.grab_set()

        try:

            self.win.attributes(
                "-topmost",
                True
            )

            self.win.after(
                100,
                lambda:
                self.win.attributes(
                    "-topmost",
                    False
                )
            )

        except Exception:
            pass

        root = ctk.CTkScrollableFrame(
            self.win
        )

        root.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=16
        )

        # =====================================================
        # TITLE
        # =====================================================

        ctk.CTkLabel(
            root,
            text=self.task.title,
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 8)
        )

        # =====================================================
        # DATE
        # =====================================================

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
            root,
            text=dt,
            text_color="#9CA3AF",
            font=ctk.CTkFont(
                size=15
            )
        ).pack(
            anchor="w",
            pady=(0, 18)
        )

        # =====================================================
        # DESCRIPTION
        # =====================================================

        ctk.CTkLabel(
            root,
            text="Описание",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.desc = ctk.CTkTextbox(
            root,
            height=180,
            corner_radius=18
        )

        self.desc.pack(
            fill="x",
            pady=(0, 10)
        )

        self.desc.insert(
            "1.0",
            getattr(
                self.task,
                "description",
                ""
            ) or ""
        )

        ctk.CTkButton(
            root,
            text="Сохранить описание",
            height=42,
            command=self.save_description
        ).pack(
            fill="x",
            pady=(0, 24)
        )

        # =====================================================
        # SUBTASKS
        # =====================================================

        ctk.CTkLabel(
            root,
            text="Подзадачи",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        self.subtasks_holder = ctk.CTkFrame(
            root,
            corner_radius=18
        )

        self.subtasks_holder.pack(
            fill="x",
            pady=(0, 18)
        )

        self.render_subtasks()

    # =====================================================
    # SUBTASKS
    # =====================================================

    def render_subtasks(self):

        for child in self.subtasks_holder.winfo_children():
            child.destroy()

        try:

            subtasks = json.loads(
                getattr(
                    self.task,
                    "subtasks_json",
                    "[]"
                )
            )

        except Exception:

            subtasks = []

        self.subtask_vars = []

        for idx, sub in enumerate(subtasks):

            var = ctk.IntVar(
                value=int(
                    sub.get(
                        "done",
                        0
                    )
                )
            )

            self.subtask_vars.append(var)

            cb = ctk.CTkCheckBox(
                self.subtasks_holder,
                text=sub.get(
                    "text",
                    ""
                ),
                variable=var,
                command=self.save_subtasks
            )

            cb.pack(
                anchor="w",
                padx=14,
                pady=10
            )

    # =====================================================
    # SAVE DESCRIPTION
    # =====================================================

    def save_description(self):

        new_desc = (
            self.desc.get(
                "1.0",
                "end"
            ).strip()
        )

        try:

            self.store.update_task(
                self.task.id,
                title=self.task.title,
                date=self.task.date,
                time_start=self.task.time_start,
                time_end=self.task.time_end,
                tag=self.task.tag,
                description=new_desc,
                subtasks_json=self.task.subtasks_json,
                remind_offsets_json=self.task.remind_offsets_json
            )

            self.task.description = new_desc

        except Exception as e:

            print(e)

    # =====================================================
    # SAVE SUBTASKS
    # =====================================================

    def save_subtasks(self):

        try:

            subtasks = json.loads(
                self.task.subtasks_json or "[]"
            )

        except Exception:

            subtasks = []

        for idx, sub in enumerate(subtasks):

            sub["done"] = int(
                self.subtask_vars[idx].get()
            )

        new_json = json.dumps(
            subtasks,
            ensure_ascii=False
        )

        try:

            self.store.update_task(
                self.task.id,
                title=self.task.title,
                date=self.task.date,
                time_start=self.task.time_start,
                time_end=self.task.time_end,
                tag=self.task.tag,
                description=self.task.description,
                subtasks_json=new_json,
                remind_offsets_json=self.task.remind_offsets_json
            )

            self.task.subtasks_json = new_json

        except Exception as e:

            print(e)