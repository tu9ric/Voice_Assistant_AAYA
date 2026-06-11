import customtkinter as ctk
from tkinter import messagebox

from .task_card import TaskCard
from .task_form import TaskForm


class TasksTab:

    def __init__(
        self,
        parent,
        store,
        on_changed=None
    ):

        self.parent = parent
        self.store = store
        self.on_changed = on_changed

        self.parent.grid_columnconfigure(
            0,
            weight=1
        )

        self.parent.grid_rowconfigure(
            1,
            weight=1
        )

        # ============================================
        # TOP BAR
        # ============================================

        top = ctk.CTkFrame(
            parent
        )

        top.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=10
        )

        top.grid_columnconfigure(
            0,
            weight=1
        )

        self.filter_entry = ctk.CTkEntry(
            top,
            placeholder_text="Фильтр YYYY-MM-DD"
        )

        self.filter_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=8
        )

        ctk.CTkButton(
            top,
            text="⟳",
            width=50,
            command=self.refresh
        ).grid(
            row=0,
            column=1,
            padx=4
        )

        ctk.CTkButton(
            top,
            text="➕ Добавить задачу",
            command=self.open_create
        ).grid(
            row=0,
            column=2,
            padx=8
        )

        # ============================================
        # LIST
        # ============================================

        self.list_frame = ctk.CTkScrollableFrame(
            parent
        )

        self.list_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        self.list_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.refresh()

    # =================================================
    # REFRESH
    # =================================================

    def refresh(self):

        for child in self.list_frame.winfo_children():
            child.destroy()

        date_filter = (
            self.filter_entry.get() or ""
        ).strip() or None

        tasks = self.store.list_tasks(
            date=date_filter,
            include_done=True
        )

        if not tasks:

            ctk.CTkLabel(
                self.list_frame,
                text="Задач нет"
            ).pack(
                pady=20
            )

            return

        for task in tasks:

            card = TaskCard(
                self.list_frame,
                task,
                self.store,
                on_edit=self.open_edit,
                on_delete=self.delete_task,
                on_toggle=self.refresh_and_notify
            )

            card.pack(
                fill="x",
                padx=4,
                pady=6
            )

    # =================================================
    # REFRESH + NOTIFY CALENDAR
    # =================================================

    def refresh_and_notify(self):

        self.refresh()

        if self.on_changed:

            try:
                self.on_changed()
            except Exception as e:
                print(e)

    # =================================================
    # CREATE
    # =================================================

    def open_create(self):

        TaskForm(
            self.parent.winfo_toplevel(),
            self.store,
            on_save=self.refresh_and_notify
        )

    # =================================================
    # EDIT
    # =================================================

    def open_edit(self, task):

        TaskForm(
            self.parent.winfo_toplevel(),
            self.store,
            on_save=self.refresh_and_notify,
            task=task
        )

    # =================================================
    # DELETE
    # =================================================

    def delete_task(self, task_id):

        ok = messagebox.askyesno(
            "TODO",
            "Удалить задачу?"
        )

        if not ok:
            return

        self.store.delete_task(
            task_id
        )

        self.refresh_and_notify()