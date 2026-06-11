import calendar
import customtkinter as ctk

from tkinter import messagebox
from datetime import date as ddate, timedelta

from .task_details import TaskDetailsWindow
from .date_picker import open_date_picker
from .calendar_utils import RU_WEEKDAY_SHORT, RU_MONTHS


# =====================================================
# CONSTANTS
# =====================================================

VIEW_MONTH = "Месяц"
VIEW_WEEK = "Неделя"
VIEW_3_DAYS = "3 дня"
VIEW_DAY = "День"


def _time_values():

    values = [
        "Без времени"
    ]

    for hour in range(
        0,
        24
    ):

        values.append(
            f"{hour:02d}:00"
        )

        values.append(
            f"{hour:02d}:30"
        )

    return values


TIME_VALUES = _time_values()


# =====================================================
# HELPERS
# =====================================================

def _format_date_ru(
    value: ddate
) -> str:

    return f"{value.day} {RU_MONTHS[value.month - 1].lower()} {value.year}"


def _format_short_date(
    value: ddate
) -> str:

    return value.strftime(
        "%d.%m.%Y"
    )


def _task_time_text(
    task
) -> str:

    start = getattr(
        task,
        "time_start",
        None
    )

    end = getattr(
        task,
        "time_end",
        None
    )

    if start and end:

        return f"{start}–{end}"

    if start:

        return start

    return "Весь день"


def _short(
    text: str,
    limit: int = 28
) -> str:

    text = (
        text
        or ""
    ).strip()

    if len(
        text
    ) > limit:

        return text[:limit].strip() + "..."

    return text


def _parse_hm(
    value: str
):

    try:

        h, m = value.split(
            ":"
        )

        return int(
            h
        ), int(
            m
        )

    except Exception:

        return None


def _sort_tasks(
    tasks
):

    def key(
        task
    ):

        done = int(
            getattr(
                task,
                "done",
                0
            )
            or 0
        )

        start = getattr(
            task,
            "time_start",
            None
        ) or "99:99"

        return (
            done,
            start,
            getattr(
                task,
                "id",
                0
            )
        )

    return sorted(
        tasks,
        key=key
    )


# =====================================================
# QUICK TASK DIALOG
# =====================================================

class QuickTaskDialog:

    def __init__(
        self,
        parent,
        store,
        task_date: ddate,
        on_save=None
    ):

        self.parent = parent
        self.store = store
        self.task_date = task_date
        self.on_save = on_save

        self._build()

    def _build(
        self
    ):

        self.win = ctk.CTkToplevel(
            self.parent
        )

        self.win.title(
            "Новая задача"
        )

        self.win.geometry(
            "640x660"
        )

        self.win.minsize(
            560,
            600
        )

        self.win.resizable(
            False,
            False
        )

        try:

            self.win.transient(
                self.parent
            )

            self.win.grab_set()
            self.win.lift()
            self.win.focus_force()

            self.win.attributes(
                "-topmost",
                True
            )

            self.win.after(
                250,
                lambda:
                self.win.attributes(
                    "-topmost",
                    False
                )
            )

        except Exception:
            pass

        try:

            self.win.update_idletasks()

            sw = self.win.winfo_screenwidth()
            sh = self.win.winfo_screenheight()

            w = 640
            h = 660

            x = int(
                (sw - w) / 2
            )

            y = int(
                (sh - h) / 2
            )

            self.win.geometry(
                f"{w}x{h}+{x}+{y}"
            )

        except Exception:
            pass

        root = ctk.CTkFrame(
            self.win,
            corner_radius=18
        )

        root.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        root.grid_columnconfigure(
            0,
            weight=1
        )

        root.grid_rowconfigure(
            5,
            weight=1
        )

        ctk.CTkLabel(
            root,
            text="Быстрая задача",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(18, 4)
        )

        self.date_label = ctk.CTkLabel(
            root,
            text=_format_date_ru(
                self.task_date
            ),
            font=ctk.CTkFont(
                size=14
            ),
            text_color="#A8A8A8"
        )

        self.date_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=18,
            pady=(0, 16)
        )

        self.title_entry = ctk.CTkEntry(
            root,
            height=46,
            corner_radius=14,
            placeholder_text="Название задачи"
        )

        self.title_entry.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 14)
        )

        time_block = ctk.CTkFrame(
            root,
            fg_color="transparent"
        )

        time_block.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 14)
        )

        time_block.grid_columnconfigure(
            0,
            weight=1
        )

        time_block.grid_columnconfigure(
            1,
            weight=1
        )

        start_block = ctk.CTkFrame(
            time_block,
            fg_color="transparent"
        )

        start_block.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        start_block.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            start_block,
            text="Начало",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#A8A8A8"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4)
        )

        self.start_menu = ctk.CTkOptionMenu(
            start_block,
            height=42,
            corner_radius=14,
            values=TIME_VALUES
        )

        self.start_menu.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.start_menu.set(
            "Без времени"
        )

        end_block = ctk.CTkFrame(
            time_block,
            fg_color="transparent"
        )

        end_block.grid(
            row=0,
            column=1,
            sticky="ew"
        )

        end_block.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            end_block,
            text="Конец",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#A8A8A8"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4)
        )

        self.end_menu = ctk.CTkOptionMenu(
            end_block,
            height=42,
            corner_radius=14,
            values=TIME_VALUES
        )

        self.end_menu.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.end_menu.set(
            "Без времени"
        )

        self.tag_entry = ctk.CTkEntry(
            root,
            height=42,
            corner_radius=14,
            placeholder_text="Тег, например Учёба / Работа / Дом"
        )

        self.tag_entry.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 14)
        )

        desc_block = ctk.CTkFrame(
            root,
            fg_color="transparent"
        )

        desc_block.grid(
            row=5,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(0, 16)
        )

        desc_block.grid_columnconfigure(
            0,
            weight=1
        )

        desc_block.grid_rowconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            desc_block,
            text="Описание",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#A8A8A8"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4)
        )

        self.desc_box = ctk.CTkTextbox(
            desc_block,
            corner_radius=14
        )

        self.desc_box.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        buttons = ctk.CTkFrame(
            root,
            fg_color="transparent"
        )

        buttons.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 18)
        )

        buttons.grid_columnconfigure(
            0,
            weight=1
        )

        buttons.grid_columnconfigure(
            1,
            weight=1
        )

        ctk.CTkButton(
            buttons,
            text="Отмена",
            height=44,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=self.win.destroy
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        ctk.CTkButton(
            buttons,
            text="Сохранить",
            height=44,
            corner_radius=14,
            command=self._save
        ).grid(
            row=0,
            column=1,
            sticky="ew"
        )

        self.title_entry.focus()

    def _save(
        self
    ):

        title = (
            self.title_entry.get()
            or ""
        ).strip()

        if not title:

            messagebox.showwarning(
                "Календарь",
                "Введите название задачи."
            )

            return

        time_start = self.start_menu.get()
        time_end = self.end_menu.get()

        if time_start == "Без времени":

            time_start = None

        if time_end == "Без времени":

            time_end = None

        if time_end and not time_start:

            messagebox.showwarning(
                "Календарь",
                "Если указано время окончания, нужно указать время начала."
            )

            return

        if time_start and time_end:

            if time_end <= time_start:

                messagebox.showwarning(
                    "Календарь",
                    "Время окончания должно быть позже времени начала."
                )

                return

        tag = (
            self.tag_entry.get()
            or ""
        ).strip() or None

        desc = (
            self.desc_box.get(
                "1.0",
                "end"
            )
            or ""
        ).strip()

        try:

            self.store.create_task(
                title=title,
                date=self.task_date.isoformat(),
                time_start=time_start,
                time_end=time_end,
                tag=tag,
                description=desc
            )

        except Exception as e:

            messagebox.showerror(
                "Календарь",
                str(
                    e
                )
            )

            return

        if self.on_save:

            self.on_save()

        self.win.destroy()


# =====================================================
# CALENDAR TAB
# =====================================================

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

        self.view = VIEW_MONTH
        self.selected_date = ddate.today()

        self.current_month_date = self.selected_date.replace(
            day=1
        )

        self.parent.grid_columnconfigure(
            0,
            weight=1
        )

        self.parent.grid_rowconfigure(
            0,
            weight=1
        )

        self._build_ui()
        self.refresh()

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(
        self
    ):

        self.root = ctk.CTkFrame(
            self.parent,
            corner_radius=22
        )

        self.root.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=16
        )

        self.root.grid_columnconfigure(
            0,
            weight=1
        )

        self.root.grid_rowconfigure(
            2,
            weight=1
        )

        # =================================================
        # HEADER
        # =================================================

        header = ctk.CTkFrame(
            self.root,
            corner_radius=18
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=16,
            pady=(16, 10)
        )

        header.grid_columnconfigure(
            0,
            weight=1
        )

        left = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        left.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=14
        )

        self.title_label = ctk.CTkLabel(
            left,
            text="Календарь",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        self.title_label.pack(
            anchor="w"
        )

        self.subtitle_label = ctk.CTkLabel(
            left,
            text="",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        )

        self.subtitle_label.pack(
            anchor="w",
            pady=(2, 0)
        )

        right = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        right.grid(
            row=0,
            column=1,
            sticky="e",
            padx=18,
            pady=14
        )

        ctk.CTkButton(
            right,
            text="Сегодня",
            width=96,
            height=38,
            corner_radius=14,
            command=self._today
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ctk.CTkButton(
            right,
            text="←",
            width=48,
            height=38,
            corner_radius=14,
            command=self._prev
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ctk.CTkButton(
            right,
            text="→",
            width=48,
            height=38,
            corner_radius=14,
            command=self._next
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ctk.CTkButton(
            right,
            text="📅 Дата",
            width=100,
            height=38,
            corner_radius=14,
            command=self._open_date_picker
        ).pack(
            side="left"
        )

        # =================================================
        # TOOLBAR
        # =================================================

        toolbar = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )

        toolbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 10)
        )

        toolbar.grid_columnconfigure(
            0,
            weight=0
        )

        toolbar.grid_columnconfigure(
            1,
            weight=1
        )

        try:

            self.view_switch = ctk.CTkSegmentedButton(
                toolbar,
                values=[
                    VIEW_MONTH,
                    VIEW_WEEK,
                    VIEW_3_DAYS,
                    VIEW_DAY
                ],
                command=self._change_view
            )

            self.view_switch.set(
                self.view
            )

            self.view_switch.grid(
                row=0,
                column=0,
                sticky="w"
            )

        except Exception:

            self.view_switch = ctk.CTkOptionMenu(
                toolbar,
                values=[
                    VIEW_MONTH,
                    VIEW_WEEK,
                    VIEW_3_DAYS,
                    VIEW_DAY
                ],
                command=self._change_view,
                width=160
            )

            self.view_switch.set(
                self.view
            )

            self.view_switch.grid(
                row=0,
                column=0,
                sticky="w"
            )

        self.stats_label = ctk.CTkLabel(
            toolbar,
            text="",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        )

        self.stats_label.grid(
            row=0,
            column=1,
            sticky="e"
        )

        # =================================================
        # CONTENT
        # =================================================

        self.content = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )

        self.content.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 16)
        )

        self.content.grid_columnconfigure(
            0,
            weight=1
        )

        self.content.grid_columnconfigure(
            1,
            weight=0
        )

        self.content.grid_rowconfigure(
            0,
            weight=1
        )

        self.calendar_panel = ctk.CTkFrame(
            self.content,
            corner_radius=18
        )

        self.calendar_panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 12)
        )

        self.calendar_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self.calendar_panel.grid_rowconfigure(
            0,
            weight=1
        )

        self.day_panel = ctk.CTkFrame(
            self.content,
            width=380,
            corner_radius=18
        )

        self.day_panel.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.day_panel.grid_propagate(
            False
        )

        self.day_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self.day_panel.grid_rowconfigure(
            2,
            weight=1
        )

    # =====================================================
    # NAVIGATION
    # =====================================================

    def _change_view(
        self,
        value
    ):

        self.view = value

        if self.view == VIEW_MONTH:

            self.current_month_date = self.selected_date.replace(
                day=1
            )

        self.refresh()

    def _today(
        self
    ):

        self.selected_date = ddate.today()
        self.current_month_date = self.selected_date.replace(
            day=1
        )

        self.refresh()

    def _prev(
        self
    ):

        if self.view == VIEW_MONTH:

            first = self.current_month_date.replace(
                day=1
            )

            prev_last = first - timedelta(
                days=1
            )

            self.current_month_date = prev_last.replace(
                day=1
            )

            self.selected_date = self.current_month_date

        elif self.view == VIEW_WEEK:

            self.selected_date -= timedelta(
                days=7
            )

            self.current_month_date = self.selected_date.replace(
                day=1
            )

        elif self.view == VIEW_3_DAYS:

            self.selected_date -= timedelta(
                days=3
            )

            self.current_month_date = self.selected_date.replace(
                day=1
            )

        else:

            self.selected_date -= timedelta(
                days=1
            )

            self.current_month_date = self.selected_date.replace(
                day=1
            )

        self.refresh()

    def _next(
        self
    ):

        if self.view == VIEW_MONTH:

            y = self.current_month_date.year
            m = self.current_month_date.month

            if m == 12:

                y += 1
                m = 1

            else:

                m += 1

            self.current_month_date = ddate(
                y,
                m,
                1
            )

            self.selected_date = self.current_month_date

        elif self.view == VIEW_WEEK:

            self.selected_date += timedelta(
                days=7
            )

            self.current_month_date = self.selected_date.replace(
                day=1
            )

        elif self.view == VIEW_3_DAYS:

            self.selected_date += timedelta(
                days=3
            )

            self.current_month_date = self.selected_date.replace(
                day=1
            )

        else:

            self.selected_date += timedelta(
                days=1
            )

            self.current_month_date = self.selected_date.replace(
                day=1
            )

        self.refresh()

    def _open_date_picker(
        self
    ):

        open_date_picker(
            self.parent,
            self.selected_date,
            self._set_date
        )

    def _set_date(
        self,
        new_date
    ):

        self.selected_date = new_date
        self.current_month_date = new_date.replace(
            day=1
        )

        self.refresh()

    # =====================================================
    # DATA
    # =====================================================

    def _tasks_for_day(
        self,
        day: ddate,
        include_done: bool = True
    ):

        try:

            return _sort_tasks(
                self.store.list_tasks(
                    date=day.isoformat(),
                    include_done=include_done
                )
            )

        except Exception:

            return []

    def _month_days(
        self
    ):

        first = self.current_month_date.replace(
            day=1
        )

        start = first - timedelta(
            days=first.weekday()
        )

        return [
            start + timedelta(
                days=i
            )
            for i in range(
                42
            )
        ]

    def _visible_days(
        self
    ):

        if self.view == VIEW_WEEK:

            start = self.selected_date - timedelta(
                days=self.selected_date.weekday()
            )

            return [
                start + timedelta(
                    days=i
                )
                for i in range(
                    7
                )
            ]

        if self.view == VIEW_3_DAYS:

            return [
                self.selected_date + timedelta(
                    days=i
                )
                for i in range(
                    3
                )
            ]

        if self.view == VIEW_DAY:

            return [
                self.selected_date
            ]

        return self._month_days()

    def _month_stats(
        self
    ):

        first = self.current_month_date.replace(
            day=1
        )

        _, days_count = calendar.monthrange(
            first.year,
            first.month
        )

        total = 0
        done = 0
        today_count = 0

        today = ddate.today()

        for i in range(
            days_count
        ):

            day = first + timedelta(
                days=i
            )

            tasks = self._tasks_for_day(
                day,
                include_done=True
            )

            total += len(
                tasks
            )

            done += len(
                [
                    task
                    for task in tasks
                    if int(
                        getattr(
                            task,
                            "done",
                            0
                        )
                        or 0
                    )
                ]
            )

            if day == today:

                today_count = len(
                    tasks
                )

        return total, done, today_count

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self
    ):

        try:

            if hasattr(
                self,
                "view_switch"
            ):

                self.view_switch.set(
                    self.view
                )

        except Exception:
            pass

        self._update_header()

        for child in self.calendar_panel.winfo_children():

            child.destroy()

        for child in self.day_panel.winfo_children():

            child.destroy()

        if self.view == VIEW_MONTH:

            self._render_month_view()

        else:

            self._render_range_view()

        self._render_day_panel()

    def _update_header(
        self
    ):

        if self.view == VIEW_MONTH:

            shown = self.current_month_date

            self.title_label.configure(
                text=f"{RU_MONTHS[shown.month - 1]} {shown.year}"
            )

            self.subtitle_label.configure(
                text=f"Выбрано: {_format_date_ru(self.selected_date)}"
            )

        elif self.view == VIEW_WEEK:

            start = self.selected_date - timedelta(
                days=self.selected_date.weekday()
            )

            end = start + timedelta(
                days=6
            )

            self.title_label.configure(
                text=f"{_format_short_date(start)} — {_format_short_date(end)}"
            )

            self.subtitle_label.configure(
                text="Недельный обзор задач"
            )

        elif self.view == VIEW_3_DAYS:

            end = self.selected_date + timedelta(
                days=2
            )

            self.title_label.configure(
                text=f"{_format_short_date(self.selected_date)} — {_format_short_date(end)}"
            )

            self.subtitle_label.configure(
                text="Ближайшие 3 дня"
            )

        else:

            self.title_label.configure(
                text=_format_date_ru(
                    self.selected_date
                )
            )

            self.subtitle_label.configure(
                text=f"{RU_WEEKDAY_SHORT[self.selected_date.weekday()]}, дневной план"
            )

        total, done, today_count = self._month_stats()

        selected_tasks = self._tasks_for_day(
            self.selected_date,
            include_done=True
        )

        self.stats_label.configure(
            text=(
                f"Месяц: {total} задач · выполнено {done} · "
                f"сегодня {today_count} · выбрано {len(selected_tasks)}"
            )
        )

    # =====================================================
    # MONTH VIEW
    # =====================================================

    def _render_month_view(
        self
    ):

        root = ctk.CTkFrame(
            self.calendar_panel,
            fg_color="transparent"
        )

        root.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=12,
            pady=12
        )

        root.grid_columnconfigure(
            tuple(
                range(
                    7
                )
            ),
            weight=1
        )

        for row in range(
            7
        ):

            root.grid_rowconfigure(
                row,
                weight=1
            )

        for col, weekday in enumerate(
            RU_WEEKDAY_SHORT
        ):

            label = ctk.CTkLabel(
                root,
                text=weekday.upper(),
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                ),
                text_color="#A8A8A8"
            )

            label.grid(
                row=0,
                column=col,
                padx=4,
                pady=(0, 8),
                sticky="ew"
            )

        days = self._month_days()

        for index, day in enumerate(
            days
        ):

            row = index // 7 + 1
            col = index % 7

            self._add_day_cell(
                root,
                row,
                col,
                day
            )

    def _add_day_cell(
        self,
        root,
        row: int,
        col: int,
        day: ddate
    ):

        today = ddate.today()

        is_today = day == today
        is_selected = day == self.selected_date

        is_current_month = (
            day.month == self.current_month_date.month
        )

        tasks = self._tasks_for_day(
            day,
            include_done=True
        )

        bg = "#24262B"

        if not is_current_month:

            bg = "#1D1E22"

        if is_selected:

            bg = "#1F6AA5"

        elif is_today:

            bg = "#25324A"

        card = ctk.CTkFrame(
            root,
            corner_radius=16,
            fg_color=bg,
            border_width=(
                2
                if is_selected
                else 1
            ),
            border_color=(
                "#7FD1FF"
                if is_selected
                else "#34363D"
            )
        )

        card.grid(
            row=row,
            column=col,
            padx=5,
            pady=5,
            sticky="nsew"
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        top = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        top.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=9,
            pady=(9, 4)
        )

        top.grid_columnconfigure(
            0,
            weight=1
        )

        day_label = ctk.CTkLabel(
            top,
            text=str(
                day.day
            ),
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color=(
                "#FFFFFF"
                if is_current_month
                else "#777777"
            )
        )

        day_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        if tasks:

            count_label = ctk.CTkLabel(
                top,
                text=f"{len(tasks)}",
                width=26,
                height=22,
                corner_radius=11,
                fg_color=(
                    "#7FD1FF"
                    if is_selected
                    else "#1F6AA5"
                ),
                text_color="#FFFFFF",
                font=ctk.CTkFont(
                    size=12,
                    weight="bold"
                )
            )

            count_label.grid(
                row=0,
                column=1,
                sticky="e"
            )

        if is_today:

            today_label = ctk.CTkLabel(
                card,
                text="Сегодня",
                font=ctk.CTkFont(
                    size=11
                ),
                text_color="#7CFF95",
                anchor="w"
            )

            today_label.grid(
                row=1,
                column=0,
                sticky="ew",
                padx=9,
                pady=(0, 2)
            )

        task_container = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        task_container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(2, 8)
        )

        task_container.grid_columnconfigure(
            0,
            weight=1
        )

        for i, task in enumerate(
            tasks[:3]
        ):

            done = bool(
                int(
                    getattr(
                        task,
                        "done",
                        0
                    )
                    or 0
                )
            )

            task_label = ctk.CTkLabel(
                task_container,
                text=(
                    f"{_task_time_text(task)} · {_short(task.title, 22)}"
                    if getattr(
                        task,
                        "time_start",
                        None
                    )
                    else _short(
                        task.title,
                        26
                    )
                ),
                font=ctk.CTkFont(
                    size=11
                ),
                text_color=(
                    "#A8A8A8"
                    if done
                    else "#FFFFFF"
                ),
                fg_color=(
                    "#353535"
                    if done
                    else "#2E86DE"
                ),
                corner_radius=8,
                anchor="w",
                padx=8
            )

            task_label.grid(
                row=i,
                column=0,
                sticky="ew",
                pady=2
            )

            task_label.bind(
                "<Button-1>",
                lambda event, t=task:
                self._open_task(
                    t
                )
            )

        if len(
            tasks
        ) > 3:

            more_label = ctk.CTkLabel(
                task_container,
                text=f"+ ещё {len(tasks) - 3}",
                font=ctk.CTkFont(
                    size=11
                ),
                text_color="#A8A8A8",
                anchor="w"
            )

            more_label.grid(
                row=4,
                column=0,
                sticky="ew",
                pady=(3, 0)
            )

        for widget in (
            card,
            top,
            day_label,
            task_container
        ):

            widget.bind(
                "<Button-1>",
                lambda event, d=day:
                self._select_day(
                    d
                )
            )

            widget.bind(
                "<Double-Button-1>",
                lambda event, d=day:
                self._new_task_for_day(
                    d
                )
            )

    # =====================================================
    # RANGE VIEW
    # =====================================================

    def _render_range_view(
        self
    ):

        days = self._visible_days()

        root = ctk.CTkScrollableFrame(
            self.calendar_panel,
            corner_radius=16
        )

        root.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=12,
            pady=12
        )

        root.grid_columnconfigure(
            0,
            weight=1
        )

        for index, day in enumerate(
            days
        ):

            self._add_day_agenda_block(
                root,
                index,
                day
            )

    def _add_day_agenda_block(
        self,
        parent,
        row: int,
        day: ddate
    ):

        today = ddate.today()
        is_today = day == today
        is_selected = day == self.selected_date

        tasks = self._tasks_for_day(
            day,
            include_done=True
        )

        active = len(
            [
                task
                for task in tasks
                if not int(
                    getattr(
                        task,
                        "done",
                        0
                    )
                    or 0
                )
            ]
        )

        done = len(
            tasks
        ) - active

        card = ctk.CTkFrame(
            parent,
            corner_radius=18,
            fg_color=(
                "#25324A"
                if is_today
                else "#24262B"
            ),
            border_width=(
                2
                if is_selected
                else 1
            ),
            border_color=(
                "#7FD1FF"
                if is_selected
                else "#34363D"
            )
        )

        card.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=6,
            pady=8
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        header = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=16,
            pady=(14, 8)
        )

        header.grid_columnconfigure(
            0,
            weight=1
        )

        title_text = (
            f"{RU_WEEKDAY_SHORT[day.weekday()]}, {_format_date_ru(day)}"
        )

        title_label = ctk.CTkLabel(
            header,
            text=title_text,
            font=ctk.CTkFont(
                size=19,
                weight="bold"
            ),
            anchor="w"
        )

        title_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        badges = []

        if is_today:

            badges.append(
                "Сегодня"
            )

        badges.append(
            f"{len(tasks)} задач"
        )

        badges.append(
            f"активных {active}"
        )

        badges.append(
            f"выполнено {done}"
        )

        badge_label = ctk.CTkLabel(
            header,
            text=" · ".join(
                badges
            ),
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#A8A8A8",
            anchor="e"
        )

        badge_label.grid(
            row=0,
            column=1,
            sticky="e",
            padx=(10, 0)
        )

        action_row = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        action_row.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 8)
        )

        action_row.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkButton(
            action_row,
            text="➕ Добавить задачу на этот день",
            height=36,
            corner_radius=12,
            command=lambda d=day:
            self._new_task_for_day(
                d
            )
        ).grid(
            row=0,
            column=0,
            sticky="ew"
        )

        tasks_container = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        tasks_container.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 12)
        )

        tasks_container.grid_columnconfigure(
            0,
            weight=1
        )

        if not tasks:

            empty = ctk.CTkLabel(
                tasks_container,
                text="На этот день задач нет.",
                font=ctk.CTkFont(
                    size=14
                ),
                text_color="#A8A8A8",
                anchor="w"
            )

            empty.grid(
                row=0,
                column=0,
                sticky="ew",
                padx=8,
                pady=12
            )

        else:

            for index, task in enumerate(
                tasks
            ):

                self._add_task_card(
                    tasks_container,
                    index,
                    task,
                    compact=False
                )

        for widget in (
            card,
            header,
            title_label,
            badge_label
        ):

            widget.bind(
                "<Button-1>",
                lambda event, d=day:
                self._select_day(
                    d
                )
            )

    # =====================================================
    # DAY PANEL
    # =====================================================

    def _render_day_panel(
        self
    ):

        day = self.selected_date

        header = ctk.CTkFrame(
            self.day_panel,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=16,
            pady=(16, 10)
        )

        header.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            header,
            text="Выбранный день",
            font=ctk.CTkFont(
                size=14
            ),
            text_color="#A8A8A8"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            header,
            text=str(
                day.day
            ),
            font=ctk.CTkFont(
                size=42,
                weight="bold"
            )
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(2, 0)
        )

        ctk.CTkLabel(
            header,
            text=f"{RU_WEEKDAY_SHORT[day.weekday()]}, {_format_date_ru(day)}",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        ).grid(
            row=2,
            column=0,
            sticky="w"
        )

        actions = ctk.CTkFrame(
            self.day_panel,
            fg_color="transparent"
        )

        actions.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 10)
        )

        actions.grid_columnconfigure(
            0,
            weight=1
        )

        actions.grid_columnconfigure(
            1,
            weight=1
        )

        ctk.CTkButton(
            actions,
            text="➕ Новая задача",
            height=38,
            corner_radius=14,
            command=lambda:
            self._new_task_for_day(
                day
            )
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        ctk.CTkButton(
            actions,
            text="↻ Обновить",
            height=38,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=self.refresh
        ).grid(
            row=0,
            column=1,
            sticky="ew"
        )

        tasks_box = ctk.CTkScrollableFrame(
            self.day_panel,
            corner_radius=14
        )

        tasks_box.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

        tasks_box.grid_columnconfigure(
            0,
            weight=1
        )

        tasks = self._tasks_for_day(
            day,
            include_done=True
        )

        active = len(
            [
                task
                for task in tasks
                if not int(
                    getattr(
                        task,
                        "done",
                        0
                    )
                    or 0
                )
            ]
        )

        done = len(
            tasks
        ) - active

        summary = ctk.CTkLabel(
            tasks_box,
            text=f"Всего: {len(tasks)} · активных: {active} · выполнено: {done}",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#A8A8A8",
            anchor="w"
        )

        summary.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(10, 8)
        )

        if not tasks:

            empty = ctk.CTkFrame(
                tasks_box,
                corner_radius=14,
                fg_color="#24262B"
            )

            empty.grid(
                row=1,
                column=0,
                sticky="ew",
                padx=6,
                pady=8
            )

            ctk.CTkLabel(
                empty,
                text="На этот день задач нет.\nСоздай новую задачу кнопкой выше.",
                font=ctk.CTkFont(
                    size=14
                ),
                text_color="#A8A8A8",
                justify="left",
                wraplength=310
            ).pack(
                padx=16,
                pady=18,
                anchor="w"
            )

            return

        for index, task in enumerate(
            tasks,
            start=1
        ):

            self._add_task_card(
                tasks_box,
                index,
                task,
                compact=True
            )

    def _add_task_card(
        self,
        parent,
        row: int,
        task,
        compact: bool = False
    ):

        done = bool(
            int(
                getattr(
                    task,
                    "done",
                    0
                )
                or 0
            )
        )

        card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color=(
                "#303030"
                if done
                else "#24262B"
            ),
            border_width=1,
            border_color=(
                "#3A3A3A"
                if done
                else "#34363D"
            )
        )

        card.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=6,
            pady=6
        )

        card.grid_columnconfigure(
            1,
            weight=1
        )

        done_var = ctk.IntVar(
            value=1 if done else 0
        )

        checkbox = ctk.CTkCheckBox(
            card,
            text="",
            width=24,
            variable=done_var,
            command=lambda t=task, var=done_var:
            self._toggle_done(
                t,
                var.get()
            )
        )

        checkbox.grid(
            row=0,
            column=0,
            rowspan=3,
            padx=(12, 6),
            pady=12,
            sticky="n"
        )

        title = ctk.CTkLabel(
            card,
            text=task.title,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            text_color=(
                "#A8A8A8"
                if done
                else "#FFFFFF"
            ),
            anchor="w",
            justify="left",
            wraplength=(
                270
                if compact
                else 520
            )
        )

        title.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=(12, 2)
        )

        meta_parts = [
            _task_time_text(
                task
            )
        ]

        if getattr(
            task,
            "tag",
            None
        ):

            meta_parts.append(
                f"#{task.tag}"
            )

        meta = ctk.CTkLabel(
            card,
            text=" · ".join(
                meta_parts
            ),
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#A8A8A8",
            anchor="w"
        )

        meta.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=(0, 8)
        )

        btn_row = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        btn_row.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=(0, 12)
        )

        ctk.CTkButton(
            btn_row,
            text="Открыть",
            height=30,
            width=86,
            corner_radius=10,
            command=lambda t=task:
            self._open_task(
                t
            )
        ).pack(
            side="left",
            padx=(0, 6)
        )

        ctk.CTkButton(
            btn_row,
            text="Удалить",
            height=30,
            width=86,
            corner_radius=10,
            fg_color="#8B0000",
            hover_color="#5E0000",
            command=lambda t=task:
            self._delete_task(
                t
            )
        ).pack(
            side="left"
        )

        for widget in (
            card,
            title,
            meta
        ):

            widget.bind(
                "<Double-Button-1>",
                lambda event, t=task:
                self._open_task(
                    t
                )
            )

    # =====================================================
    # ACTIONS
    # =====================================================

    def _select_day(
        self,
        day: ddate
    ):

        self.selected_date = day
        self.current_month_date = day.replace(
            day=1
        )

        self.refresh()

    def _new_task_for_day(
        self,
        day: ddate = None
    ):

        day = day or self.selected_date

        self.selected_date = day
        self.current_month_date = day.replace(
            day=1
        )

        QuickTaskDialog(
            self.parent.winfo_toplevel(),
            self.store,
            day,
            on_save=self._after_task_changed
        )

    def _open_task(
        self,
        task
    ):

        TaskDetailsWindow(
            self.parent.winfo_toplevel(),
            task,
            self.store,
            self._after_task_changed
        )

    def _toggle_done(
        self,
        task,
        value
    ):

        try:

            if hasattr(
                self.store,
                "set_done"
            ):

                self.store.set_done(
                    task.id,
                    1 if value else 0
                )

            else:

                self.store.update_task_done(
                    task.id,
                    1 if value else 0
                )

            self._after_task_changed()

        except Exception as e:

            messagebox.showerror(
                "Календарь",
                str(
                    e
                )
            )

    def _delete_task(
        self,
        task
    ):

        if not messagebox.askyesno(
            "Календарь",
            f"Удалить задачу «{task.title}»?"
        ):

            return

        try:

            self.store.delete_task(
                task.id
            )

            self._after_task_changed()

        except Exception as e:

            messagebox.showerror(
                "Календарь",
                str(
                    e
                )
            )

    def _after_task_changed(
        self
    ):

        self.refresh()

        if self.on_tasks_changed:

            try:

                self.on_tasks_changed()

            except Exception as e:

                print(
                    e
                )