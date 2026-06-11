import customtkinter as ctk
import json


OPENED_TASK_WINDOWS = {}


class TaskDetailsWindow:

    def __init__(
        self,
        parent,
        task,
        store=None,
        on_refresh=None
    ):

        self.parent = parent
        self.task = task
        self.task_id = task.id
        self.store = store
        self.on_refresh_callbacks = []

        if on_refresh:
            self.on_refresh_callbacks.append(on_refresh)

        self.subtask_vars = []
        self.status_label = None
        self.desc_box = None
        self.root = None
        self.win = None

        # =====================================================
        # ЕСЛИ ОКНО ЭТОЙ ЗАДАЧИ УЖЕ ОТКРЫТО — НЕ СОЗДАЁМ НОВОЕ
        # =====================================================

        existing_window = OPENED_TASK_WINDOWS.get(
            self.task_id
        )

        if existing_window:

            try:

                if (
                    hasattr(existing_window, "win")
                    and existing_window.win
                    and existing_window.win.winfo_exists()
                ):

                    if (
                        on_refresh
                        and on_refresh not in existing_window.on_refresh_callbacks
                    ):
                        existing_window.on_refresh_callbacks.append(
                            on_refresh
                        )

                    if store:
                        existing_window.store = store

                    existing_window.refresh_from_store()

                    existing_window.win.lift()
                    existing_window.win.focus_force()

                    try:
                        existing_window.win.attributes(
                            "-topmost",
                            True
                        )

                        existing_window.win.after(
                            120,
                            lambda:
                            existing_window.win.attributes(
                                "-topmost",
                                False
                            )
                        )
                    except Exception:
                        pass

                    self.win = existing_window.win

                    return

            except Exception:
                pass

        OPENED_TASK_WINDOWS[
            self.task_id
        ] = self

        self.build()

    # =====================================================
    # BUILD
    # =====================================================

    def build(self):

        self.win = ctk.CTkToplevel(
            self.parent
        )

        self.win.title(
            self.task.title
        )

        self.win.geometry(
            "860x820"
        )

        self.win.minsize(
            620,
            620
        )

        self.win.lift()
        self.win.focus_force()

        # ВАЖНО:
        # grab_set НЕ используем.
        # Иначе окно становится модальным и мешает открыть эту же задачу
        # из календаря / задач.

        try:
            self.win.attributes(
                "-topmost",
                True
            )

            self.win.after(
                120,
                lambda:
                self.win.attributes(
                    "-topmost",
                    False
                )
            )
        except Exception:
            pass

        self.win.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        self.root = ctk.CTkScrollableFrame(
            self.win,
            corner_radius=0
        )

        self.root.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        self.render_content()

    # =====================================================
    # RENDER
    # =====================================================

    def render_content(self):

        if not self.root:
            return

        for child in self.root.winfo_children():
            child.destroy()

        self.subtask_vars = []

        root = self.root

        ctk.CTkLabel(
            root,
            text=self.task.title,
            font=ctk.CTkFont(
                size=32,
                weight="bold"
            ),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 10)
        )

        dt = self.task.date

        if getattr(
            self.task,
            "time_start",
            None
        ):

            dt += f"  {self.task.time_start}"

            if getattr(
                self.task,
                "time_end",
                None
            ):

                dt += f" - {self.task.time_end}"

        ctk.CTkLabel(
            root,
            text=dt,
            text_color="#9CA3AF",
            font=ctk.CTkFont(
                size=18
            ),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 24)
        )

        ctk.CTkLabel(
            root,
            text="Описание",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 10)
        )

        self.desc_box = ctk.CTkTextbox(
            root,
            height=260,
            corner_radius=18
        )

        self.desc_box.pack(
            fill="x",
            pady=(0, 28)
        )

        self.desc_box.insert(
            "1.0",
            getattr(
                self.task,
                "description",
                ""
            ) or ""
        )

        ctk.CTkLabel(
            root,
            text="Подзадачи",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 12)
        )

        self.subtasks_holder = ctk.CTkFrame(
            root,
            corner_radius=18
        )

        self.subtasks_holder.pack(
            fill="x",
            pady=(0, 24)
        )

        self.render_subtasks()

        if getattr(
            self.task,
            "tag",
            None
        ):

            ctk.CTkLabel(
                root,
                text=self.task.tag,
                height=36,
                corner_radius=18,
                fg_color="#2563EB",
                padx=16
            ).pack(
                anchor="w",
                pady=(0, 24)
            )

        self.status_label = ctk.CTkLabel(
            root,
            text="",
            text_color="#22C55E",
            font=ctk.CTkFont(
                size=14
            )
        )

        self.status_label.pack(
            fill="x",
            pady=(0, 8)
        )

        ctk.CTkButton(
            root,
            text="Сохранить изменения",
            height=52,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            command=self.save_changes
        ).pack(
            fill="x",
            pady=(0, 20)
        )

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
                ) or "[]"
            )
        except Exception:
            subtasks = []

        if not subtasks:

            ctk.CTkLabel(
                self.subtasks_holder,
                text="Нет подзадач",
                text_color="#9CA3AF"
            ).pack(
                anchor="w",
                padx=16,
                pady=16
            )

            return

        for sub in subtasks:

            row = ctk.CTkFrame(
                self.subtasks_holder,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                padx=14,
                pady=8
            )

            var = ctk.IntVar(
                value=int(
                    sub.get(
                        "done",
                        0
                    )
                )
            )

            cb = ctk.CTkCheckBox(
                row,
                text=sub.get(
                    "text",
                    ""
                ),
                variable=var,
                command=self.save_subtasks_only
            )

            cb.pack(
                anchor="w"
            )

            self.subtask_vars.append(
                (
                    var,
                    sub
                )
            )

    # =====================================================
    # CURRENT DATA
    # =====================================================

    def get_description(self):

        if not self.desc_box:
            return getattr(
                self.task,
                "description",
                ""
            ) or ""

        return self.desc_box.get(
            "1.0",
            "end"
        ).strip()

    def get_subtasks_json(self):

        subtasks = []

        for var, sub in self.subtask_vars:

            subtasks.append({
                "text": sub.get(
                    "text",
                    ""
                ),
                "done": int(
                    var.get()
                )
            })

        return json.dumps(
            subtasks,
            ensure_ascii=False
        )

    # =====================================================
    # SAVE SUBTASKS
    # =====================================================

    def save_subtasks_only(self):

        if not self.store:
            return

        subtasks_json = self.get_subtasks_json()

        try:
            self.store.update_task(
                self.task.id,
                subtasks_json=subtasks_json
            )

            self.task.subtasks_json = subtasks_json

            if self.status_label:
                self.status_label.configure(
                    text="Подзадачи сохранены",
                    text_color="#22C55E"
                )

        except Exception as e:

            print(e)

            if self.status_label:
                self.status_label.configure(
                    text=f"Ошибка сохранения подзадач: {e}",
                    text_color="#EF4444"
                )

            return

        self.call_refresh_callbacks()

    # =====================================================
    # SAVE ALL
    # =====================================================

    def save_changes(self):

        if not self.store:

            if self.status_label:
                self.status_label.configure(
                    text="Ошибка: хранилище задач не передано",
                    text_color="#EF4444"
                )

            return

        description = self.get_description()
        subtasks_json = self.get_subtasks_json()

        try:
            self.store.update_task(
                self.task.id,
                title=self.task.title,
                date=self.task.date,
                time_start=self.task.time_start,
                time_end=self.task.time_end,
                tag=self.task.tag,
                description=description,
                subtasks_json=subtasks_json,
                remind_offsets_json=self.task.remind_offsets_json
            )

            self.task.description = description
            self.task.subtasks_json = subtasks_json

            if self.status_label:
                self.status_label.configure(
                    text="Изменения сохранены",
                    text_color="#22C55E"
                )

        except Exception as e:

            print(e)

            if self.status_label:
                self.status_label.configure(
                    text=f"Ошибка сохранения: {e}",
                    text_color="#EF4444"
                )

            return

        self.call_refresh_callbacks()

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_from_store(self):

        if not self.store:
            return

        try:
            fresh = self.store.get_task(
                self.task_id
            )
        except Exception as e:
            print(e)
            return

        if not fresh:
            return

        self.task = fresh
        self.render_content()

    def call_refresh_callbacks(self):

        for callback in list(
            self.on_refresh_callbacks
        ):

            try:
                if callback:
                    callback()
            except Exception as e:
                print(e)

    # =====================================================
    # CLOSE
    # =====================================================

    def on_close(self):

        try:
            current = OPENED_TASK_WINDOWS.get(
                self.task_id
            )

            if current is self:
                del OPENED_TASK_WINDOWS[
                    self.task_id
                ]

        except Exception:
            pass

        try:
            self.win.destroy()
        except Exception:
            pass