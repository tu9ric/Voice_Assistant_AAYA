import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date as ddate
import json

HOURS = [f"{h:02d}" for h in range(24)]
MINUTES = ["00", "15", "30", "45"]

REMINDER_PRESETS = [
    ("Без напоминания", None),
    ("За 1 день", "P1D"),
    ("За 1 час", "PT1H"),
    ("За 30 минут", "PT30M"),
    ("За 15 минут", "PT15M"),
    ("За 5 минут", "PT5M"),
]


def _hm(h: str, m: str) -> str:
    return f"{h}:{m}"


def _parse_hm(s: str):
    h, m = s.split(":")
    return int(h), int(m)


def _minutes(hm: str) -> int:
    h, m = _parse_hm(hm)
    return h * 60 + m


class TaskWindow(ctk.CTkToplevel):

    def __init__(self, parent, store, on_save=None, task=None):
        super().__init__(parent)

        self.store = store
        self.on_save = on_save
        self.task = task
        self.editing = task is not None

        self.description_text = ""
        self.subtasks_data = []

        if self.editing:
            self.description_text = task.description or ""

            try:
                self.subtasks_data = json.loads(task.subtasks_json or "[]")
            except Exception:
                self.subtasks_data = []

        self.title(
            "Редактирование задачи"
            if self.editing
            else "Новая задача"
        )

        self.geometry("760x820")
        self.minsize(700, 760)

        self.grab_set()

        self.build_ui()

    def build_ui(self):

        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        container.grid_columnconfigure(0, weight=1)

        # HEADER
        ctk.CTkLabel(
            container,
            text="Редактирование задачи"
            if self.editing
            else "Создание задачи",
            font=ctk.CTkFont(size=30, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 25))

        # TITLE
        self.e_title = ctk.CTkEntry(
            container,
            placeholder_text="Название задачи",
            height=54,
            font=ctk.CTkFont(size=18)
        )
        self.e_title.grid(row=1, column=0, sticky="ew", pady=(0, 18))

        if self.editing:
            self.e_title.insert(0, self.task.title or "")

        # DATE
        self.date_var = ctk.StringVar(
            value=(
                self.task.date
                if self.editing
                else ddate.today().isoformat()
            )
        )

        self.e_date = ctk.CTkEntry(
            container,
            textvariable=self.date_var,
            height=50
        )
        self.e_date.grid(row=2, column=0, sticky="ew", pady=(0, 18))

        # TIME
        time_frame = ctk.CTkFrame(container)
        time_frame.grid(row=3, column=0, sticky="ew", pady=(0, 18))

        self.all_day_var = ctk.IntVar(
            value=1 if self.editing and not self.task.time_start else 0
        )

        ctk.CTkCheckBox(
            time_frame,
            text="Весь день",
            variable=self.all_day_var
        ).pack(anchor="w", padx=12, pady=(12, 6))

        row = ctk.CTkFrame(time_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 12))

        self.start_h = ctk.CTkOptionMenu(row, values=HOURS)
        self.start_h.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.start_m = ctk.CTkOptionMenu(row, values=MINUTES)
        self.start_m.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.end_h = ctk.CTkOptionMenu(row, values=HOURS)
        self.end_h.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.end_m = ctk.CTkOptionMenu(row, values=MINUTES)
        self.end_m.pack(side="left", expand=True, fill="x")

        self.start_h.set("09")
        self.start_m.set("00")
        self.end_h.set("10")
        self.end_m.set("00")

        # REMINDER
        reminder_values = [x[0] for x in REMINDER_PRESETS]

        self.reminder_menu = ctk.CTkOptionMenu(
            container,
            values=reminder_values,
            height=50
        )
        self.reminder_menu.grid(row=4, column=0, sticky="ew", pady=(0, 18))

        self.reminder_menu.set("Без напоминания")

        # TAG
        self.e_tag = ctk.CTkEntry(
            container,
            placeholder_text="Тег",
            height=50
        )
        self.e_tag.grid(row=5, column=0, sticky="ew", pady=(0, 18))

        if self.editing and self.task.tag:
            self.e_tag.insert(0, self.task.tag)

        # DESCRIPTION
        ctk.CTkButton(
            container,
            text="✏ Описание",
            height=50,
            command=self.open_description_window
        ).grid(row=6, column=0, sticky="ew", pady=(0, 18))

        # SUBTASKS
        ctk.CTkButton(
            container,
            text="📝 Подзадачи",
            height=50,
            command=self.open_subtasks_window
        ).grid(row=7, column=0, sticky="ew", pady=(0, 18))

        # SAVE
        ctk.CTkButton(
            container,
            text="Сохранить",
            height=56,
            command=self.save_task
        ).grid(row=8, column=0, sticky="ew", pady=(0, 24))

    def open_description_window(self):

        win = ctk.CTkToplevel(self)

        win.title("Описание")
        win.geometry("700x500")
        win.grab_set()

        textbox = ctk.CTkTextbox(win)
        textbox.pack(fill="both", expand=True, padx=20, pady=20)

        textbox.insert("1.0", self.description_text)

        def save():
            self.description_text = textbox.get(
                "1.0",
                "end"
            ).strip()

            win.destroy()

        ctk.CTkButton(
            win,
            text="Сохранить",
            command=save
        ).pack(fill="x", padx=20, pady=(0, 20))

    def open_subtasks_window(self):

        win = ctk.CTkToplevel(self)

        win.title("Подзадачи")
        win.geometry("600x500")
        win.grab_set()

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        items = []

        def add_subtask(text="", done=0):

            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=6)

            row.grid_columnconfigure(1, weight=1)

            done_var = ctk.IntVar(value=int(done))

            ctk.CTkCheckBox(
                row,
                text="",
                variable=done_var
            ).grid(row=0, column=0, padx=8, pady=8)

            entry = ctk.CTkEntry(
                row,
                placeholder_text="Подзадача..."
            )
            entry.grid(row=0, column=1, sticky="ew", padx=8, pady=8)

            if text:
                entry.insert(0, text)

            items.append((done_var, entry))

        for item in self.subtasks_data:
            add_subtask(
                item.get("text", ""),
                item.get("done", 0)
            )

        ctk.CTkButton(
            win,
            text="＋ Добавить подзадачу",
            command=lambda: add_subtask("")
        ).pack(fill="x", padx=20, pady=(0, 10))

        def save():
            result = []

            for var, entry in items:
                text = (entry.get() or "").strip()

                if text:
                    result.append({
                        "text": text,
                        "done": int(var.get())
                    })

            self.subtasks_data = result

            win.destroy()

        ctk.CTkButton(
            win,
            text="Сохранить",
            command=save
        ).pack(fill="x", padx=20, pady=(0, 20))

    def save_task(self):

        title = (self.e_title.get() or "").strip()
        date_s = (self.date_var.get() or "").strip()

        if not title:
            messagebox.showerror(
                "TODO",
                "Введите название задачи."
            )
            return

        try:
            datetime.strptime(date_s, "%Y-%m-%d")
        except Exception:
            messagebox.showerror(
                "TODO",
                "Дата должна быть YYYY-MM-DD."
            )
            return

        if self.all_day_var.get() == 1:
            t1 = None
            t2 = None
        else:
            t1 = _hm(
                self.start_h.get(),
                self.start_m.get()
            )

            t2 = _hm(
                self.end_h.get(),
                self.end_m.get()
            )

            if _minutes(t2) <= _minutes(t1):
                messagebox.showerror(
                    "TODO",
                    "Конец должен быть позже начала."
                )
                return

        reminder_name = self.reminder_menu.get()

        offsets = []

        for name, code in REMINDER_PRESETS:
            if name == reminder_name and code:
                offsets = [code]

        remind_offsets_json = json.dumps(
            offsets,
            ensure_ascii=False
        )

        subtasks_json = json.dumps(
            self.subtasks_data,
            ensure_ascii=False
        )

        try:

            if self.editing:

                self.store.update_task(
                    self.task.id,
                    title=title,
                    date=date_s,
                    time_start=t1,
                    time_end=t2,
                    tag=(self.e_tag.get() or "").strip() or None,
                    description=self.description_text,
                    subtasks_json=subtasks_json,
                    remind_offsets_json=remind_offsets_json,
                )

            else:

                self.store.create_task(
                    title,
                    date_s,
                    t1,
                    t2,
                    (self.e_tag.get() or "").strip() or None,
                    self.description_text,
                    subtasks_json=subtasks_json,
                    remind_offsets_json=remind_offsets_json
                )

        except Exception as e:
            messagebox.showerror("TODO", str(e))
            return

        if self.on_save:
            self.on_save()

        self.destroy()