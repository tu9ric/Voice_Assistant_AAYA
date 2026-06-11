import customtkinter as ctk

from tkinter import messagebox
from datetime import date as ddate, datetime

from .task_form import TaskForm
from .task_details import TaskDetailsWindow


# =====================================================
# HELPERS
# =====================================================

VIEW_ACTIVE = "Активные"
VIEW_ARCHIVE = "Архив"


def _today_iso() -> str:

    return ddate.today().isoformat()


def _format_date(
    value: str
) -> str:

    try:

        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).strftime(
            "%d.%m.%Y"
        )

    except Exception:

        return value or ""


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
    limit: int = 130
) -> str:

    text = (
        text
        or ""
    ).strip()

    text = " ".join(
        text.split()
    )

    if len(
        text
    ) > limit:

        return text[:limit].strip() + "..."

    return text


def _sort_tasks(
    tasks
):

    def key(
        task
    ):

        date_value = getattr(
            task,
            "date",
            ""
        ) or ""

        time_value = getattr(
            task,
            "time_start",
            None
        ) or "99:99"

        return (
            date_value,
            time_value,
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


def _is_overdue(
    task
) -> bool:

    if int(
        getattr(
            task,
            "done",
            0
        )
        or 0
    ):

        return False

    task_date = getattr(
        task,
        "date",
        ""
    ) or ""

    return task_date < _today_iso()


def _is_today(
    task
) -> bool:

    return (
        getattr(
            task,
            "date",
            ""
        )
        or ""
    ) == _today_iso()


# =====================================================
# TASKS TAB
# =====================================================

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

        self.current_view = VIEW_ACTIVE
        self.search_text = ""
        self.date_filter = ""
        self.tag_filter = ""

        self._search_after_id = None

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
            3,
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
            pady=16
        )

        ctk.CTkLabel(
            left,
            text="Задачи",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).pack(
            anchor="w"
        )

        self.subtitle_label = ctk.CTkLabel(
            left,
            text="Планирование, контроль и архив выполненных задач",
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
            pady=16
        )

        self.new_task_btn = ctk.CTkButton(
            right,
            text="➕ Новая задача",
            height=40,
            width=150,
            corner_radius=14,
            command=self.open_create
        )

        self.new_task_btn.pack(
            side="left",
            padx=(0, 8)
        )

        self.refresh_btn = ctk.CTkButton(
            right,
            text="↻",
            height=40,
            width=48,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=self.refresh
        )

        self.refresh_btn.pack(
            side="left"
        )

        # =================================================
        # STATS
        # =================================================

        self.stats_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )

        self.stats_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 10)
        )

        for i in range(
            4
        ):

            self.stats_frame.grid_columnconfigure(
                i,
                weight=1
            )

        self.card_total = self._create_stat_card(
            self.stats_frame,
            0,
            "Всего",
            "0"
        )

        self.card_active = self._create_stat_card(
            self.stats_frame,
            1,
            "Активные",
            "0"
        )

        self.card_today = self._create_stat_card(
            self.stats_frame,
            2,
            "Сегодня",
            "0"
        )

        self.card_archive = self._create_stat_card(
            self.stats_frame,
            3,
            "Архив",
            "0"
        )

        # =================================================
        # TOOLBAR
        # =================================================

        toolbar = ctk.CTkFrame(
            self.root,
            corner_radius=18
        )

        toolbar.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 10)
        )

        toolbar.grid_columnconfigure(
            1,
            weight=1
        )

        self.view_switch = ctk.CTkSegmentedButton(
            toolbar,
            values=[
                VIEW_ACTIVE,
                VIEW_ARCHIVE
            ],
            command=self._change_view
        )

        self.view_switch.set(
            self.current_view
        )

        self.view_switch.grid(
            row=0,
            column=0,
            padx=14,
            pady=14,
            sticky="w"
        )

        self.search_entry = ctk.CTkEntry(
            toolbar,
            height=40,
            corner_radius=14,
            placeholder_text="Поиск по названию, описанию или тегу..."
        )

        self.search_entry.grid(
            row=0,
            column=1,
            padx=(0, 10),
            pady=14,
            sticky="ew"
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self._on_filter_change
        )

        self.date_entry = ctk.CTkEntry(
            toolbar,
            height=40,
            width=135,
            corner_radius=14,
            placeholder_text="YYYY-MM-DD"
        )

        self.date_entry.grid(
            row=0,
            column=2,
            padx=(0, 10),
            pady=14
        )

        self.date_entry.bind(
            "<KeyRelease>",
            self._on_filter_change
        )

        self.today_btn = ctk.CTkButton(
            toolbar,
            text="Сегодня",
            height=40,
            width=92,
            corner_radius=14,
            command=self._filter_today
        )

        self.today_btn.grid(
            row=0,
            column=3,
            padx=(0, 10),
            pady=14
        )

        self.clear_filter_btn = ctk.CTkButton(
            toolbar,
            text="Очистить",
            height=40,
            width=100,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=self._clear_filters
        )

        self.clear_filter_btn.grid(
            row=0,
            column=4,
            padx=(0, 14),
            pady=14
        )

        # =================================================
        # CONTENT
        # =================================================

        self.content = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )

        self.content.grid(
            row=3,
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

        self.list_panel = ctk.CTkFrame(
            self.content,
            corner_radius=18
        )

        self.list_panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 12)
        )

        self.list_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self.list_panel.grid_rowconfigure(
            1,
            weight=1
        )

        list_header = ctk.CTkFrame(
            self.list_panel,
            fg_color="transparent"
        )

        list_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=16,
            pady=(14, 8)
        )

        list_header.grid_columnconfigure(
            0,
            weight=1
        )

        self.list_title = ctk.CTkLabel(
            list_header,
            text="Активные задачи",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )

        self.list_title.grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.list_count = ctk.CTkLabel(
            list_header,
            text="",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        )

        self.list_count.grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.tasks_list = ctk.CTkScrollableFrame(
            self.list_panel,
            corner_radius=14
        )

        self.tasks_list.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

        self.tasks_list.grid_columnconfigure(
            0,
            weight=1
        )

        # =================================================
        # RIGHT INFO PANEL
        # =================================================

        self.info_panel = ctk.CTkFrame(
            self.content,
            width=340,
            corner_radius=18
        )

        self.info_panel.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.info_panel.grid_propagate(
            False
        )

        self.info_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self._build_info_panel()

    def _create_stat_card(
        self,
        parent,
        column: int,
        title: str,
        value: str
    ):

        card = ctk.CTkFrame(
            parent,
            corner_radius=18
        )

        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=(
                0
                if column == 0
                else 8,
                0
            ),
            pady=0
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#A8A8A8"
        ).pack(
            anchor="w",
            padx=14,
            pady=(12, 2)
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        )

        value_label.pack(
            anchor="w",
            padx=14,
            pady=(0, 12)
        )

        return value_label

    def _build_info_panel(
        self
    ):

        ctk.CTkLabel(
            self.info_panel,
            text="Панель задач",
            font=ctk.CTkFont(
                size=21,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(18, 6)
        )

        self.info_text = ctk.CTkLabel(
            self.info_panel,
            text=(
                "Выполненные задачи автоматически попадают в архив.\n\n"
                "В активном списке остаются только задачи, которые ещё нужно сделать."
            ),
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8",
            justify="left",
            wraplength=290
        )

        self.info_text.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 14)
        )

        quick = ctk.CTkFrame(
            self.info_panel,
            corner_radius=16
        )

        quick.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 14)
        )

        quick.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            quick,
            text="Быстрые действия",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=14,
            pady=(14, 8)
        )

        ctk.CTkButton(
            quick,
            text="➕ Новая задача",
            height=38,
            corner_radius=14,
            command=self.open_create
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 8)
        )

        ctk.CTkButton(
            quick,
            text="📅 Показать сегодня",
            height=38,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=self._filter_today
        ).grid(
            row=2,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 8)
        )

        ctk.CTkButton(
            quick,
            text="🗄 Открыть архив",
            height=38,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=lambda:
            self._change_view(
                VIEW_ARCHIVE
            )
        ).grid(
            row=3,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 14)
        )

        hint = ctk.CTkFrame(
            self.info_panel,
            corner_radius=16
        )

        hint.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 14)
        )

        ctk.CTkLabel(
            hint,
            text="Как работает архив?",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=14,
            pady=(14, 6)
        )

        ctk.CTkLabel(
            hint,
            text=(
                "1. Отметь задачу галочкой.\n"
                "2. Она исчезнет из активных.\n"
                "3. Найти её можно в разделе «Архив».\n"
                "4. Из архива её можно восстановить."
            ),
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8",
            justify="left",
            wraplength=290
        ).pack(
            anchor="w",
            padx=14,
            pady=(0, 14)
        )

    # =====================================================
    # FILTERS
    # =====================================================

    def _change_view(
        self,
        value
    ):

        self.current_view = value

        try:

            self.view_switch.set(
                value
            )

        except Exception:
            pass

        self.refresh()

    def _on_filter_change(
        self,
        event=None
    ):

        if self._search_after_id:

            try:

                self.parent.after_cancel(
                    self._search_after_id
                )

            except Exception:
                pass

        self._search_after_id = self.parent.after(
            250,
            self.refresh
        )

    def _filter_today(
        self
    ):

        self.date_entry.delete(
            0,
            "end"
        )

        self.date_entry.insert(
            0,
            _today_iso()
        )

        self.refresh()

    def _clear_filters(
        self
    ):

        self.search_entry.delete(
            0,
            "end"
        )

        self.date_entry.delete(
            0,
            "end"
        )

        self.refresh()

    # =====================================================
    # DATA
    # =====================================================

    def _get_all_tasks(
        self
    ):

        try:

            return self.store.list_tasks(
                include_done=True
            )

        except TypeError:

            return self.store.list_tasks()

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )

            return []

    def _get_visible_tasks(
        self
    ):

        tasks = self._get_all_tasks()

        query = (
            self.search_entry.get()
            or ""
        ).strip().lower()

        date_filter = (
            self.date_entry.get()
            or ""
        ).strip()

        result = []

        for task in tasks:

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

            if self.current_view == VIEW_ACTIVE and done:

                continue

            if self.current_view == VIEW_ARCHIVE and not done:

                continue

            if date_filter:

                if (
                    getattr(
                        task,
                        "date",
                        ""
                    )
                    or ""
                ) != date_filter:

                    continue

            if query:

                haystack = " ".join(
                    [
                        getattr(
                            task,
                            "title",
                            ""
                        )
                        or "",
                        getattr(
                            task,
                            "description",
                            ""
                        )
                        or "",
                        getattr(
                            task,
                            "tag",
                            ""
                        )
                        or "",
                        getattr(
                            task,
                            "date",
                            ""
                        )
                        or "",
                    ]
                ).lower()

                if query not in haystack:

                    continue

            result.append(
                task
            )

        return _sort_tasks(
            result
        )

    def _stats(
        self
    ):

        tasks = self._get_all_tasks()

        total = len(
            tasks
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

        archive = total - active

        today = len(
            [
                task
                for task in tasks
                if (
                    getattr(
                        task,
                        "date",
                        ""
                    )
                    or ""
                ) == _today_iso()
                and not int(
                    getattr(
                        task,
                        "done",
                        0
                    )
                    or 0
                )
            ]
        )

        return total, active, today, archive

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self
    ):

        for child in self.tasks_list.winfo_children():

            child.destroy()

        total, active, today, archive = self._stats()

        self.card_total.configure(
            text=str(
                total
            )
        )

        self.card_active.configure(
            text=str(
                active
            )
        )

        self.card_today.configure(
            text=str(
                today
            )
        )

        self.card_archive.configure(
            text=str(
                archive
            )
        )

        visible_tasks = self._get_visible_tasks()

        if self.current_view == VIEW_ACTIVE:

            self.list_title.configure(
                text="Активные задачи"
            )

            self.subtitle_label.configure(
                text="Выполненные задачи автоматически перемещаются в архив"
            )

        else:

            self.list_title.configure(
                text="Архив выполненных задач"
            )

            self.subtitle_label.configure(
                text="Здесь хранятся завершённые задачи"
            )

        self.list_count.configure(
            text=f"Показано: {len(visible_tasks)}"
        )

        if not self.store.get_current_user():

            self._show_empty_state(
                "Сначала войдите в аккаунт, чтобы работать с задачами."
            )

            return

        if not visible_tasks:

            if self.current_view == VIEW_ACTIVE:

                self._show_empty_state(
                    "Активных задач нет.\nСоздай новую задачу или очисти фильтры."
                )

            else:

                self._show_empty_state(
                    "Архив пуст.\nВыполненные задачи будут попадать сюда автоматически."
                )

            return

        for index, task in enumerate(
            visible_tasks
        ):

            self._add_task_card(
                index,
                task
            )

    def refresh_and_notify(
        self
    ):

        self.refresh()

        if self.on_changed:

            try:

                self.on_changed()

            except Exception as e:

                print(
                    e
                )

    def _show_empty_state(
        self,
        text: str
    ):

        box = ctk.CTkFrame(
            self.tasks_list,
            corner_radius=18,
            fg_color="#24262B"
        )

        box.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=12
        )

        ctk.CTkLabel(
            box,
            text=text,
            font=ctk.CTkFont(
                size=15
            ),
            text_color="#A8A8A8",
            justify="left",
            wraplength=620
        ).pack(
            padx=18,
            pady=22,
            anchor="w"
        )

    # =====================================================
    # TASK CARD
    # =====================================================

    def _add_task_card(
        self,
        row: int,
        task
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

        overdue = _is_overdue(
            task
        )

        today = _is_today(
            task
        )

        card = ctk.CTkFrame(
            self.tasks_list,
            corner_radius=18,
            fg_color=(
                "#303030"
                if done
                else "#24262B"
            ),
            border_width=1,
            border_color=(
                "#5E1F1F"
                if overdue
                else "#2D6A4F"
                if today and not done
                else "#34363D"
            )
        )

        card.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=8,
            pady=7
        )

        card.grid_columnconfigure(
            1,
            weight=1
        )

        # =================================================
        # CHECKBOX
        # =================================================

        done_var = ctk.IntVar(
            value=1 if done else 0
        )

        checkbox = ctk.CTkCheckBox(
            card,
            text="",
            width=26,
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
            rowspan=4,
            padx=(14, 8),
            pady=16,
            sticky="n"
        )

        # =================================================
        # CONTENT
        # =================================================

        title = getattr(
            task,
            "title",
            ""
        ) or "Без названия"

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color=(
                "#A8A8A8"
                if done
                else "#FFFFFF"
            ),
            justify="left",
            anchor="w",
            wraplength=720
        )

        title_label.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 12),
            pady=(14, 2)
        )

        meta_items = [
            f"📅 {_format_date(getattr(task, 'date', ''))}",
            f"⏱ {_task_time_text(task)}"
        ]

        tag = getattr(
            task,
            "tag",
            None
        )

        if tag:

            meta_items.append(
                f"🏷 {tag}"
            )

        if overdue:

            meta_items.append(
                "⚠ просрочено"
            )

        if today and not done:

            meta_items.append(
                "сегодня"
            )

        meta_label = ctk.CTkLabel(
            card,
            text=" · ".join(
                meta_items
            ),
            font=ctk.CTkFont(
                size=12
            ),
            text_color=(
                "#FF7B7B"
                if overdue
                else "#7CFF95"
                if today and not done
                else "#A8A8A8"
            ),
            anchor="w"
        )

        meta_label.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 12),
            pady=(0, 6)
        )

        desc = _short(
            getattr(
                task,
                "description",
                ""
            ),
            160
        )

        if desc:

            desc_label = ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(
                    size=13
                ),
                text_color="#C8C8C8",
                justify="left",
                anchor="w",
                wraplength=720
            )

            desc_label.grid(
                row=2,
                column=1,
                sticky="ew",
                padx=(0, 12),
                pady=(0, 8)
            )

        # =================================================
        # BUTTONS
        # =================================================

        btn_row = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        btn_row.grid(
            row=3,
            column=1,
            sticky="ew",
            padx=(0, 12),
            pady=(0, 14)
        )

        ctk.CTkButton(
            btn_row,
            text="Открыть",
            height=32,
            width=95,
            corner_radius=11,
            command=lambda t=task:
            self.open_details(
                t
            )
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ctk.CTkButton(
            btn_row,
            text="Изменить",
            height=32,
            width=95,
            corner_radius=11,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=lambda t=task:
            self.open_edit(
                t
            )
        ).pack(
            side="left",
            padx=(0, 8)
        )

        if done:

            ctk.CTkButton(
                btn_row,
                text="Восстановить",
                height=32,
                width=120,
                corner_radius=11,
                fg_color="#2D6A4F",
                hover_color="#24583F",
                command=lambda t=task:
                self.restore_task(
                    t
                )
            ).pack(
                side="left",
                padx=(0, 8)
            )

        else:

            ctk.CTkButton(
                btn_row,
                text="В архив",
                height=32,
                width=95,
                corner_radius=11,
                fg_color="#2D6A4F",
                hover_color="#24583F",
                command=lambda t=task:
                self.archive_task(
                    t
                )
            ).pack(
                side="left",
                padx=(0, 8)
            )

        ctk.CTkButton(
            btn_row,
            text="Удалить",
            height=32,
            width=95,
            corner_radius=11,
            fg_color="#8B0000",
            hover_color="#5E0000",
            command=lambda t=task:
            self.delete_task(
                t.id
            )
        ).pack(
            side="left"
        )

        for widget in (
            card,
            title_label,
            meta_label
        ):

            widget.bind(
                "<Double-Button-1>",
                lambda event, t=task:
                self.open_details(
                    t
                )
            )

    # =====================================================
    # ACTIONS
    # =====================================================

    def open_create(
        self
    ):

        TaskForm(
            self.parent,
            self.store,
            on_save=self.refresh_and_notify
        )

    def open_edit(
        self,
        task
    ):

        TaskForm(
            self.parent,
            self.store,
            on_save=self.refresh_and_notify,
            task=task
        )

    def open_details(
        self,
        task
    ):

        TaskDetailsWindow(
            self.parent.winfo_toplevel(),
            task,
            self.store,
            self.refresh_and_notify
        )

    def _toggle_done(
        self,
        task,
        value
    ):

        try:

            self.store.update_task_done(
                task.id,
                1 if value else 0
            )

            self.refresh_and_notify()

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )

    def archive_task(
        self,
        task
    ):

        try:

            self.store.update_task_done(
                task.id,
                1
            )

            self.refresh_and_notify()

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )

    def restore_task(
        self,
        task
    ):

        try:

            self.store.update_task_done(
                task.id,
                0
            )

            self.current_view = VIEW_ACTIVE

            try:

                self.view_switch.set(
                    VIEW_ACTIVE
                )

            except Exception:
                pass

            self.refresh_and_notify()

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )

    def delete_task(
        self,
        task_id
    ):

        ok = messagebox.askyesno(
            "TODO",
            "Удалить задачу окончательно?"
        )

        if not ok:
            return

        try:

            self.store.delete_task(
                task_id
            )

            self.refresh_and_notify()

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )