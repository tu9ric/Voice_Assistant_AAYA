import customtkinter as ctk

from datetime import date as ddate, timedelta
from .task_details import TaskDetailsWindow

from .agenda_view import AgendaView
from .month_view import MonthView
from .date_picker import open_date_picker


class CalendarTab:

    def __init__(
        self,
        parent,
        store,
        on_tasks_changed=None
    ):

        self.parent = parent
        self.store = store
        self.on_tasks_changed = on_tasks_changed

        self.view = "Месяц"
        self.selected_date = ddate.today()

        self.parent.grid_columnconfigure(
            0,
            weight=1
        )

        self.parent.grid_rowconfigure(
            1,
            weight=1
        )

        # =================================================
        # TOP PANEL
        # =================================================

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
            2,
            weight=1
        )

        self.view_menu = ctk.CTkOptionMenu(
            top,
            values=[
                "Месяц",
                "Неделя",
                "3 дня",
                "День"
            ],
            command=self._change_view,
            width=140
        )

        self.view_menu.set(
            self.view
        )

        self.view_menu.grid(
            row=0,
            column=0,
            padx=(10, 8),
            pady=10,
            sticky="w"
        )

        self.btn_prev = ctk.CTkButton(
            top,
            text="◀",
            width=46,
            command=self._prev
        )

        self.btn_prev.grid(
            row=0,
            column=1,
            padx=4,
            pady=10
        )

        self.lbl_date = ctk.CTkLabel(
            top,
            text="",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        self.lbl_date.grid(
            row=0,
            column=2,
            sticky="w",
            padx=10
        )

        self.btn_next = ctk.CTkButton(
            top,
            text="▶",
            width=46,
            command=self._next
        )

        self.btn_next.grid(
            row=0,
            column=3,
            padx=4,
            pady=10
        )

        self.btn_pick = ctk.CTkButton(
            top,
            text="📅 Выбрать дату",
            command=self._open_date_picker,
            width=170
        )

        self.btn_pick.grid(
            row=0,
            column=4,
            padx=(10, 10),
            pady=10,
            sticky="e"
        )

        # =================================================
        # CONTENT
        # =================================================

        self.content = ctk.CTkFrame(
            parent,
            corner_radius=18
        )

        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        self.content.grid_columnconfigure(
            0,
            weight=1
        )

        self.content.grid_rowconfigure(
            0,
            weight=1
        )

        self.refresh()

    # =====================================================
    # CHANGE VIEW
    # =====================================================

    def _change_view(
        self,
        value
    ):

        self.view = value
        self.refresh()

    # =====================================================
    # NAVIGATION
    # =====================================================

    def _prev(self):

        if self.view == "Месяц":

            first = self.selected_date.replace(
                day=1
            )

            prev_last = first - timedelta(
                days=1
            )

            self.selected_date = prev_last.replace(
                day=1
            )

        elif self.view == "Неделя":

            self.selected_date -= timedelta(
                days=7
            )

        elif self.view == "3 дня":

            self.selected_date -= timedelta(
                days=3
            )

        else:

            self.selected_date -= timedelta(
                days=1
            )

        self.refresh()

    def _next(self):

        if self.view == "Месяц":

            y = self.selected_date.year
            m = self.selected_date.month

            if m == 12:

                y += 1
                m = 1

            else:

                m += 1

            self.selected_date = ddate(
                y,
                m,
                1
            )

        elif self.view == "Неделя":

            self.selected_date += timedelta(
                days=7
            )

        elif self.view == "3 дня":

            self.selected_date += timedelta(
                days=3
            )

        else:

            self.selected_date += timedelta(
                days=1
            )

        self.refresh()

    # =====================================================
    # DATE PICKER
    # =====================================================

    def _open_date_picker(self):

        open_date_picker(
            self.parent.winfo_toplevel(),
            self.selected_date,
            self._set_date
        )

    def _set_date(
        self,
        new_date
    ):

        self.selected_date = new_date
        self.refresh()

    # =====================================================
    # OPEN TASK DETAILS
    # =====================================================

    def _open_task(
        self,
        task
    ):

        TaskDetailsWindow(
            self.parent.winfo_toplevel(),
            task,
            self.store,
            self.refresh
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        self.lbl_date.configure(
            text=self.selected_date.strftime(
                "%d-%m-%Y"
            )
        )

        for child in self.content.winfo_children():

            child.destroy()

        if self.view == "Месяц":

            MonthView(
                self.content,
                self.store,
                self.selected_date,
                self._open_task,
                self._open_day
            )

        else:

            days = (
                7 if self.view == "Неделя"
                else 3 if self.view == "3 дня"
                else 1
            )

            AgendaView(
                self.content,
                self.store,
                self.selected_date,
                days,
                self.refresh
            )

    # =====================================================
    # OPEN DAY
    # =====================================================

    def _open_day(
        self,
        day
    ):

        self.selected_date = day

        self.view = "День"

        self.view_menu.set(
            "День"
        )

        self.refresh()