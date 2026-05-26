import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import json

from .task_window import TaskWindow

REMINDER_PRESETS = [
    ("За 2 дня", "P2D"),
    ("За 1 день", "P1D"),
    ("За 5 часов", "PT5H"),
    ("За 3 часа", "PT3H"),
    ("За 1 час", "PT1H"),
    ("За 30 минут", "PT30M"),
    ("За 15 минут", "PT15M"),
    ("За 5 минут", "PT5M"),
]


def _ui_date(iso_date: str) -> str:
    try:
        return datetime.strptime(
            iso_date,
            "%Y-%m-%d"
        ).strftime("%d-%m-%Y")
    except Exception:
        return iso_date


class TasksTab:

    def __init__(self, parent, store, on_changed=None):

        self.parent = parent
        self.store = store
        self.on_changed = on_changed

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self.parent)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        top.grid_columnconfigure(0, weight=1)

        self.task_filter_date = ctk.CTkEntry(
            top,
            placeholder_text="Фильтр YYYY-MM-DD"
        )

        self.task_filter_date.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=8
        )

        ctk.CTkButton(
            top,
            text="⟳",
            width=60,
            command=self.refresh
        ).grid(row=0, column=1, padx=8, pady=8)

        ctk.CTkButton(
            top,
            text="➕ Добавить задачу",
            command=self._open_add_task
        ).grid(row=0, column=2, padx=8, pady=8)

        self.list = ctk.CTkScrollableFrame(self.parent)

        self.list.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        self.list.grid_columnconfigure(0, weight=1)

        self.refresh()

    def refresh(self):

        date_str = (
            self.task_filter_date.get() or ""
        ).strip() or None

        tasks = self.store.list_tasks(
            date=date_str,
            include_done=True
        )

        for child in self.list.winfo_children():
            child.destroy()

        if not self.store.get_current_user():

            ctk.CTkLabel(
                self.list,
                text="Войдите в аккаунт."
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=8,
                pady=8
            )

            return

        if not tasks:

            ctk.CTkLabel(
                self.list,
                text="Задач нет."
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=8,
                pady=8
            )

            return

        for i, t in enumerate(tasks):

            row = ctk.CTkFrame(self.list)

            row.grid(
                row=i,
                column=0,
                sticky="ew",
                padx=6,
                pady=6
            )

            row.grid_columnconfigure(1, weight=1)

            done_var = ctk.IntVar(
                value=int(getattr(t, "done", 0))
            )

            def _toggle(task_id=t.id, var=done_var):

                try:

                    self.store.update_task_done(
                        task_id,
                        int(var.get())
                    )

                    self.refresh()

                    if self.on_changed:
                        self.on_changed()

                except Exception as e:
                    messagebox.showerror("TODO", str(e))

            ctk.CTkCheckBox(
                row,
                text="",
                variable=done_var,
                command=_toggle
            ).grid(
                row=0,
                column=0,
                padx=8,
                pady=8,
                sticky="w"
            )

            tag = (
                f" [{t.tag}]"
                if getattr(t, "tag", None)
                else ""
            )

            when = _ui_date(t.date)

            if getattr(t, "time_start", None):

                span = t.time_start + (
                    f"–{t.time_end}"
                    if getattr(t, "time_end", None)
                    else ""
                )

                when += f" {span}"

            title = f"{t.title}{tag}"

            title_font = ctk.CTkFont(size=18)

            if int(getattr(t, "done", 0)) == 1:
                title_font.configure(overstrike=True)

            details_visible = ctk.IntVar(value=0)

            details_frame = ctk.CTkFrame(row)

            details_frame.grid(
                row=1,
                column=1,
                columnspan=3,
                sticky="ew",
                padx=6,
                pady=(0, 8)
            )

            details_frame.grid_remove()

            def toggle_details(event=None):

                if details_visible.get() == 0:
                    details_frame.grid()
                    details_visible.set(1)
                else:
                    details_frame.grid_remove()
                    details_visible.set(0)

            title_lbl = ctk.CTkLabel(
                row,
                text=title,
                font=title_font,
                cursor="hand2"
            )

            title_lbl.grid(
                row=0,
                column=1,
                sticky="w",
                padx=6
            )

            title_lbl.bind(
                "<Button-1>",
                toggle_details
            )

            ctk.CTkLabel(
                row,
                text=when
            ).grid(
                row=0,
                column=2,
                sticky="e",
                padx=8
            )

            desc = (
                getattr(t, "description", "") or ""
            ).strip()

            if desc:

                ctk.CTkLabel(
                    details_frame,
                    text=desc,
                    justify="left",
                    wraplength=500
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=(10, 8)
                )

            try:
                subtasks = json.loads(
                    getattr(t, "subtasks_json", "[]")
                )
            except Exception:
                subtasks = []

            if subtasks:

                subt_frame = ctk.CTkFrame(
                    details_frame,
                    fg_color="transparent"
                )

                subt_frame.pack(
                    fill="x",
                    padx=12,
                    pady=(0, 10)
                )

                for item in subtasks:

                    done = "☑" if item.get("done") else "☐"

                    txt = item.get("text", "")

                    ctk.CTkLabel(
                        subt_frame,
                        text=f"{done} {txt}",
                        justify="left"
                    ).pack(anchor="w", pady=2)

            rem = self._reminders_preview(
                getattr(t, "remind_offsets_json", "[]")
            )

            if rem:

                ctk.CTkLabel(
                    details_frame,
                    text=rem,
                    text_color="gray70"
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=(0, 10)
                )

            btns = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )

            btns.grid(
                row=0,
                column=3,
                padx=8,
                pady=8
            )

            ctk.CTkButton(
                btns,
                text="✏",
                width=36,
                command=lambda task=t: self._open_add_task(task)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                btns,
                text="🗑",
                width=36,
                command=lambda task_id=t.id: self._delete_task(task_id)
            ).pack(side="left", padx=4)

    def _delete_task(self, task_id):

        if not messagebox.askyesno(
            "TODO",
            "Удалить задачу?"
        ):
            return

        try:

            self.store.delete_task(task_id)

            self.refresh()

            if self.on_changed:
                self.on_changed()

        except Exception as e:
            messagebox.showerror("TODO", str(e))

    def _reminders_preview(self, offsets_json: str) -> str:

        try:

            arr = json.loads(offsets_json or "[]")

            if not arr:
                return ""

            name_by_code = {
                code: name
                for name, code in REMINDER_PRESETS
            }

            names = [
                name_by_code.get(x, x)
                for x in arr
            ]

            return "🔔 " + ", ".join(names)

        except Exception:
            return ""

    def _open_add_task(self, task=None):

        TaskWindow(
            self.parent.winfo_toplevel(),
            self.store,
            on_save=self.refresh,
            task=task
        )