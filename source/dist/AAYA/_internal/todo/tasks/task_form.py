import customtkinter as ctk
import json

from tkinter import messagebox
from datetime import date as ddate

from todo.calendar.date_picker import open_date_picker

from .task_utils import (
    HOURS,
    MINUTES,
    hm,
    minutes,
    parse_hm
)

from .subtasks_widget import SubtasksWidget
from .reminder_widget import ReminderWidget
from .task_widgets import (
    Card,
    SectionTitle
)


class TaskForm:

    def __init__(
        self,
        parent,
        store,
        on_save=None,
        task=None
    ):

        self.parent = parent
        self.store = store
        self.on_save = on_save
        self.task = task

        self.editing = task is not None

        self.build()

    # =====================================================
    # BUILD
    # =====================================================

    def build(self):

        self.win = ctk.CTkToplevel(
            self.parent
        )

        self.win.geometry("760x920")

        self.win.title(
            "Редактирование задачи"
            if self.editing
            else "Новая задача"
        )

        self.win.grab_set()
        self.win.lift()

        root = ctk.CTkScrollableFrame(
            self.win
        )

        root.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        # =================================================
        # TITLE
        # =================================================

        self.title_entry = ctk.CTkEntry(
            root,
            height=56,
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            placeholder_text="Название задачи"
        )

        self.title_entry.pack(
            fill="x",
            pady=(0, 18)
        )

        if self.editing:

            self.title_entry.insert(
                0,
                self.task.title or ""
            )

        # =================================================
        # DATE
        # =================================================

        date_card = Card(root)

        date_card.pack(
            fill="x",
            pady=(0, 16)
        )

        SectionTitle(
            date_card,
            "Дата"
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 8)
        )

        self.date_var = ctk.StringVar(
            value=(
                self.task.date
                if self.editing
                else ddate.today().isoformat()
            )
        )

        row = ctk.CTkFrame(
            date_card,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=16,
            pady=(0, 16)
        )

        self.date_btn = ctk.CTkButton(
            row,
            text=self.date_var.get(),
            height=48,
            anchor="w",
            command=self.pick_date
        )

        self.date_btn.pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkButton(
            row,
            text="📅",
            width=60,
            height=48,
            command=self.pick_date
        ).pack(
            side="left",
            padx=(8, 0)
        )

        # =================================================
        # TIME
        # =================================================

        time_card = Card(root)

        time_card.pack(
            fill="x",
            pady=(0, 16)
        )

        SectionTitle(
            time_card,
            "Время"
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 10)
        )

        body = ctk.CTkFrame(
            time_card,
            fg_color="transparent"
        )

        body.pack(
            fill="x",
            padx=16,
            pady=(0, 16)
        )

        self.all_day = ctk.IntVar(value=0)

        ctk.CTkCheckBox(
            body,
            text="Весь день",
            variable=self.all_day,
            command=self.update_time_state
        ).pack(
            anchor="w",
            pady=(0, 14)
        )

        grid = ctk.CTkFrame(
            body,
            fg_color="transparent"
        )

        grid.pack(fill="x")

        self.start_h = ctk.CTkOptionMenu(
            grid,
            values=HOURS,
            width=90
        )

        self.start_m = ctk.CTkOptionMenu(
            grid,
            values=MINUTES,
            width=90
        )

        self.end_h = ctk.CTkOptionMenu(
            grid,
            values=HOURS,
            width=90
        )

        self.end_m = ctk.CTkOptionMenu(
            grid,
            values=MINUTES,
            width=90
        )

        self.start_h.grid(
            row=0,
            column=0,
            padx=4
        )

        self.start_m.grid(
            row=0,
            column=1,
            padx=4
        )

        ctk.CTkLabel(
            grid,
            text="—",
            font=ctk.CTkFont(size=18)
        ).grid(
            row=0,
            column=2,
            padx=10
        )

        self.end_h.grid(
            row=0,
            column=3,
            padx=4
        )

        self.end_m.grid(
            row=0,
            column=4,
            padx=4
        )

        self.start_h.set("09")
        self.start_m.set("00")

        self.end_h.set("10")
        self.end_m.set("00")

        if self.editing:

            if self.task.time_start:

                sh, sm = parse_hm(
                    self.task.time_start
                )

                self.start_h.set(f"{sh:02d}")
                self.start_m.set(f"{sm:02d}")

            if self.task.time_end:

                eh, em = parse_hm(
                    self.task.time_end
                )

                self.end_h.set(f"{eh:02d}")
                self.end_m.set(f"{em:02d}")

        # =================================================
        # TAG
        # =================================================

        tag_card = Card(root)

        tag_card.pack(
            fill="x",
            pady=(0, 16)
        )

        SectionTitle(
            tag_card,
            "Тег"
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 8)
        )

        self.tag = ctk.CTkEntry(
            tag_card,
            placeholder_text="Например: Учёба / Работа / Дом"
        )

        self.tag.pack(
            fill="x",
            padx=16,
            pady=(0, 16)
        )

        if self.editing and self.task.tag:

            self.tag.insert(
                0,
                self.task.tag
            )

        # =================================================
        # REMINDER
        # =================================================

        reminder_card = Card(root)

        reminder_card.pack(
            fill="x",
            pady=(0, 16)
        )

        current_reminder = ""

        if self.editing:

            try:

                arr = json.loads(
                    self.task.remind_offsets_json or "[]"
                )

                if arr:
                    current_reminder = arr[0]

            except Exception:
                pass

        self.reminder_widget = ReminderWidget(
            reminder_card,
            current_reminder
        )

        self.reminder_widget.pack(
            fill="x",
            padx=16,
            pady=16
        )

        # =================================================
        # DESCRIPTION
        # =================================================

        desc_card = Card(root)

        desc_card.pack(
            fill="x",
            pady=(0, 16)
        )

        SectionTitle(
            desc_card,
            "Описание"
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 10)
        )

        self.desc = ctk.CTkTextbox(
            desc_card,
            height=220,
            corner_radius=16
        )

        self.desc.pack(
            fill="x",
            padx=16,
            pady=(0, 16)
        )

        if self.editing:

            self.desc.insert(
                "1.0",
                self.task.description or ""
            )

        # =================================================
        # SUBTASKS
        # =================================================

        subtasks_card = Card(root)

        subtasks_card.pack(
            fill="x",
            pady=(0, 18)
        )

        SectionTitle(
            subtasks_card,
            "Подзадачи"
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 10)
        )

        subtasks = []

        if self.editing:

            try:

                subtasks = json.loads(
                    self.task.subtasks_json or "[]"
                )

            except Exception:

                subtasks = []

        self.subtasks = SubtasksWidget(
            subtasks_card,
            subtasks
        )

        self.subtasks.pack(
            fill="x",
            padx=16,
            pady=(0, 16)
        )

        # =================================================
        # SAVE
        # =================================================

        ctk.CTkButton(
            root,
            text="Сохранить задачу",
            height=56,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            command=self.save
        ).pack(
            fill="x",
            pady=(10, 24)
        )

        self.update_time_state()

    # =====================================================
    # DATE PICKER
    # =====================================================

    def pick_date(self):

        open_date_picker(
            self.win,
            ddate.fromisoformat(
                self.date_var.get()
            ),
            self.set_date
        )

    def set_date(self, value):

        self.date_var.set(
            value.isoformat()
        )

        self.date_btn.configure(
            text=value.strftime("%d-%m-%Y")
        )

    # =====================================================
    # TIME STATE
    # =====================================================

    def update_time_state(self):

        state = (
            "disabled"
            if self.all_day.get()
            else "normal"
        )

        for w in (
            self.start_h,
            self.start_m,
            self.end_h,
            self.end_m
        ):

            w.configure(state=state)

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        title = (
            self.title_entry.get() or ""
        ).strip()

        if not title:

            messagebox.showerror(
                "TODO",
                "Введите название задачи"
            )

            return

        if self.all_day.get():

            t1 = None
            t2 = None

        else:

            t1 = hm(
                self.start_h.get(),
                self.start_m.get()
            )

            t2 = hm(
                self.end_h.get(),
                self.end_m.get()
            )

            if minutes(t2) <= minutes(t1):

                messagebox.showerror(
                    "TODO",
                    "Конец раньше начала"
                )

                return

        subtasks_json = json.dumps(
            self.subtasks.get_data(),
            ensure_ascii=False
        )

        desc = (
            self.desc.get(
                "1.0",
                "end"
            ).strip()
        )

        tag = (
            self.tag.get() or ""
        ).strip() or None

        reminder_code = (
            self.reminder_widget.get_value()
        )

        reminders_json = json.dumps(
            [reminder_code]
            if reminder_code
            else [],
            ensure_ascii=False
        )

        try:

            if self.editing:

                self.store.update_task(
                    self.task.id,
                    title=title,
                    date=self.date_var.get(),
                    time_start=t1,
                    time_end=t2,
                    tag=tag,
                    description=desc,
                    subtasks_json=subtasks_json,
                    remind_offsets_json=reminders_json
                )

            else:

                self.store.create_task(
                    title,
                    self.date_var.get(),
                    t1,
                    t2,
                    tag,
                    desc,
                    subtasks_json=subtasks_json,
                    remind_offsets_json=reminders_json
                )

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(e)
            )

            return

        if self.on_save:
            self.on_save()

        self.win.destroy()