import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date as ddate, timedelta
import json

HOURS = [f"{h:02d}" for h in range(24)]
MINUTES = ["00", "15", "30", "45"]

RU_WEEKDAY_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
RU_MONTHS = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]

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


def _hm(h: str, m: str) -> str:
    return f"{h}:{m}"


def _parse_hm(s: str) -> tuple[int, int]:
    h, m = s.split(":")
    return int(h), int(m)


def _minutes(hm: str) -> int:
    h, m = _parse_hm(hm)
    return h * 60 + m


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

        self.task_filter_date = ctk.CTkEntry(top, placeholder_text="Фильтр по дате YYYY-MM-DD (пусто = все)")
        self.task_filter_date.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(top, text="⟳", width=60, command=self.refresh).grid(row=0, column=1, padx=8, pady=8)
        ctk.CTkButton(top, text="➕ Добавить задачу", command=self._open_add_task).grid(row=0, column=2, padx=8, pady=8)

        self.list = ctk.CTkScrollableFrame(self.parent)
        self.list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.list.grid_columnconfigure(0, weight=1)

        self.refresh()

    def refresh(self):
        date_str = (self.task_filter_date.get() or "").strip() or None
        tasks = self.store.list_tasks(date=date_str, include_done=True)

        for child in self.list.winfo_children():
            child.destroy()

        if not tasks:
            ctk.CTkLabel(self.list, text="Задач нет.").grid(row=0, column=0, sticky="w", padx=8, pady=8)
            return

        for i, t in enumerate(tasks):
            row = ctk.CTkFrame(self.list)
            row.grid(row=i, column=0, sticky="ew", padx=6, pady=6)
            row.grid_columnconfigure(1, weight=1)

            done_var = ctk.IntVar(value=int(getattr(t, "done", 0)))

            def _toggle(task_id=t.id, var=done_var):
                try:
                    if hasattr(self.store, "update_task_done"):
                        self.store.update_task_done(task_id, int(var.get()))
                    else:
                        self.store.set_done(task_id, int(var.get()))
                    if self.on_changed:
                        self.on_changed()
                except Exception as e:
                    messagebox.showerror("TODO", str(e))

            ctk.CTkCheckBox(row, text="", variable=done_var, command=_toggle).grid(row=0, column=0, padx=8, pady=8, sticky="w")

            tag = f" [{t.tag}]" if getattr(t, "tag", None) else ""
            when = t.date
            if getattr(t, "time_start", None):
                span = t.time_start + (f"–{t.time_end}" if getattr(t, "time_end", None) else "")
                when += f" {span}"

            title = f"{t.title}{tag}"
            ctk.CTkLabel(row, text=title).grid(row=0, column=1, sticky="w", padx=6)
            ctk.CTkLabel(row, text=when).grid(row=0, column=2, sticky="e", padx=8)

            extra_lines = []
            desc = (getattr(t, "description", "") or "").strip()
            if desc:
                extra_lines.append(desc)

            rem = self._reminders_preview(getattr(t, "remind_offsets_json", "[]"))
            if rem:
                extra_lines.append(rem)

            if extra_lines:
                ctk.CTkLabel(row, text="\n".join(extra_lines), justify="left").grid(
                    row=1, column=1, columnspan=2, sticky="w", padx=6, pady=(0, 8)
                )

    def _reminders_preview(self, offsets_json: str) -> str:
        try:
            arr = json.loads(offsets_json or "[]")
            if not arr:
                return ""
            name_by_code = {code: name for name, code in REMINDER_PRESETS}
            names = [name_by_code.get(x, x) for x in arr]
            return "🔔 " + ", ".join(names)
        except Exception:
            return ""

    # ------------------ Dialog ------------------
    def _open_add_task(self):
        win = ctk.CTkToplevel(self.parent.winfo_toplevel())
        win.title("Добавить задачу")
        win.geometry("560x560")
        win.minsize(520, 520)
        win.grab_set()

        body = ctk.CTkFrame(win)
        body.pack(fill="both", expand=True, padx=16, pady=16)
        body.grid_columnconfigure(0, weight=1)

        # Title
        e_title = ctk.CTkEntry(body, placeholder_text="Название задачи")
        e_title.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Date row + picker
        date_row = ctk.CTkFrame(body)
        date_row.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        date_row.grid_columnconfigure(0, weight=1)

        date_var = ctk.StringVar(value=ddate.today().isoformat())
        e_date = ctk.CTkEntry(date_row, textvariable=date_var)
        e_date.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=8)

        ctk.CTkButton(date_row, text="📅", width=55, command=lambda: self._pick_date_dialog(win, date_var)).grid(
            row=0, column=1, pady=8
        )

        # Time + reminders
        time_box = ctk.CTkFrame(body)
        time_box.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        time_box.grid_columnconfigure((0, 1, 2), weight=1)

        all_day_var = ctk.IntVar(value=0)
        chk_all_day = ctk.CTkCheckBox(time_box, text="Без времени (весь день)", variable=all_day_var)
        chk_all_day.grid(row=0, column=0, columnspan=3, sticky="w", padx=8, pady=(10, 6))

        # Start (row 1)
        ctk.CTkLabel(time_box, text="Начало").grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))
        start_h = ctk.CTkOptionMenu(time_box, values=HOURS); start_h.set("09")
        start_h.grid(row=1, column=1, sticky="ew", padx=4, pady=(0, 8))
        start_m = ctk.CTkOptionMenu(time_box, values=MINUTES); start_m.set("00")
        start_m.grid(row=1, column=2, sticky="ew", padx=4, pady=(0, 8))

        # End (row 2)
        ctk.CTkLabel(time_box, text="Конец").grid(row=2, column=0, sticky="w", padx=8, pady=(0, 10))
        end_h = ctk.CTkOptionMenu(time_box, values=HOURS); end_h.set("10")
        end_h.grid(row=2, column=1, sticky="ew", padx=4, pady=(0, 10))
        end_m = ctk.CTkOptionMenu(time_box, values=MINUTES); end_m.set("00")
        end_m.grid(row=2, column=2, sticky="ew", padx=4, pady=(0, 10))

        # Reminders right under time
        rem_frame = ctk.CTkFrame(time_box)
        rem_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=8, pady=(0, 10))
        rem_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(rem_frame, text="Напоминания (можно несколько):").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(8, 6)
        )

        rem_vars = []
        for idx, (name, code) in enumerate(REMINDER_PRESETS):
            v = ctk.IntVar(value=0)
            rem_vars.append((code, v))
            r = 1 + idx // 2
            c = idx % 2
            ctk.CTkCheckBox(rem_frame, text=name, variable=v).grid(row=r, column=c, sticky="w", padx=2, pady=4)

        # Tag
        e_tag = ctk.CTkEntry(body, placeholder_text="Тег (необязательно)")
        e_tag.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Description (collapsible)
        desc_frame = ctk.CTkFrame(body)
        desc_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        desc_frame.grid_columnconfigure(0, weight=1)

        desc_open = ctk.IntVar(value=0)
        txt_desc = ctk.CTkTextbox(desc_frame, wrap="word", height=90)
        txt_desc.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        txt_desc.grid_remove()

        def toggle_desc():
            if desc_open.get() == 1:
                txt_desc.grid()
                btn_desc.configure(text="Скрыть описание")
            else:
                txt_desc.grid_remove()
                btn_desc.configure(text="Добавить описание")

        btn_desc = ctk.CTkButton(
            desc_frame, text="Добавить описание",
            command=lambda: (desc_open.set(1 - desc_open.get()), toggle_desc())
        )
        btn_desc.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        # Subtasks (compact)
        subt_frame = ctk.CTkFrame(body)
        subt_frame.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        subt_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(subt_frame, text="Подзадачи").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))

        subt_list = ctk.CTkScrollableFrame(subt_frame, height=90)
        subt_list.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        subt_list.grid_columnconfigure(0, weight=1)

        subt_items = []

        def add_subtask(text=""):
            row = ctk.CTkFrame(subt_list)
            row.pack(fill="x", padx=4, pady=4)
            row.grid_columnconfigure(1, weight=1)

            v = ctk.IntVar(value=0)
            ctk.CTkCheckBox(row, text="", variable=v).grid(row=0, column=0, padx=6, pady=6)

            e = ctk.CTkEntry(row, placeholder_text="Подзадача…")
            if text:
                e.insert(0, text)
            e.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

            subt_items.append((v, e))

        ctk.CTkButton(subt_frame, text="➕ Добавить подзадачу", command=lambda: add_subtask("")).grid(
            row=2, column=0, sticky="ew", padx=8, pady=(0, 8)
        )

        # enable/disable time + reminders when all-day
        def apply_time_state():
            state = "disabled" if all_day_var.get() == 1 else "normal"
            for w in (start_h, start_m, end_h, end_m):
                w.configure(state=state)

            # if all-day -> disable reminders and clear
            cb_state = "disabled" if all_day_var.get() == 1 else "normal"
            for child in rem_frame.winfo_children():
                if isinstance(child, ctk.CTkCheckBox):
                    child.configure(state=cb_state)
            if all_day_var.get() == 1:
                for _, v in rem_vars:
                    v.set(0)

        chk_all_day.configure(command=apply_time_state)
        apply_time_state()

        # Save
        def _save():
            title = (e_title.get() or "").strip()
            date_s = (date_var.get() or "").strip()
            tag = (e_tag.get() or "").strip() or None
            desc = (txt_desc.get("1.0", "end") or "").strip() if desc_open.get() == 1 else ""

            if not title:
                messagebox.showerror("TODO", "Введите название задачи.")
                return
            try:
                datetime.strptime(date_s, "%Y-%m-%d")
            except Exception:
                messagebox.showerror("TODO", "Дата должна быть в формате YYYY-MM-DD.")
                return

            if all_day_var.get() == 1:
                t1 = None
                t2 = None
            else:
                t1 = _hm(start_h.get(), start_m.get())
                t2 = _hm(end_h.get(), end_m.get())
                if _minutes(t2) <= _minutes(t1):
                    messagebox.showerror("TODO", "Время окончания должно быть позже времени начала.")
                    return

            # subtasks json
            subt = []
            for v, e in subt_items:
                text = (e.get() or "").strip()
                if text:
                    subt.append({"text": text, "done": int(v.get())})
            subt_json = json.dumps(subt, ensure_ascii=False)

            # reminders (multi-select)
            offsets = [code for code, v in rem_vars if v.get() == 1]
            remind_offsets_json = json.dumps(offsets, ensure_ascii=False)

            try:
                self.store.create_task(
                    title, date_s, t1, t2, tag, desc,
                    subt_json=subt_json,
                    remind_offsets_json=remind_offsets_json
                )
            except TypeError:
                # если внезапно старый store
                self.store.create_task(title, date_s, t1, t2, tag, desc)
            except Exception as e:
                messagebox.showerror("TODO", str(e))
                return

            win.destroy()
            self.refresh()
            if self.on_changed:
                self.on_changed()

        ctk.CTkButton(body, text="Сохранить", command=_save).grid(row=6, column=0, sticky="ew", pady=(6, 0))

    # ---------- Date picker ----------
    def _pick_date_dialog(self, host, date_var: ctk.StringVar):
        win = ctk.CTkToplevel(host)
        win.title("Выбор даты")
        win.geometry("420x420")
        win.grab_set()

        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(2, weight=1)

        try:
            base = datetime.strptime(date_var.get(), "%Y-%m-%d").date()
        except Exception:
            base = ddate.today()

        cur_year = base.year
        cur_month = base.month

        top = ctk.CTkFrame(win)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        years = [str(y) for y in range(cur_year - 30, cur_year + 31)]
        months = RU_MONTHS[:]

        year_menu = ctk.CTkOptionMenu(top, values=years)
        year_menu.set(str(cur_year))
        year_menu.grid(row=0, column=0, padx=8, pady=8)

        month_menu = ctk.CTkOptionMenu(top, values=months)
        month_menu.set(RU_MONTHS[cur_month - 1])
        month_menu.grid(row=0, column=1, padx=8, pady=8)

        def get_month_date():
            y = int(year_menu.get())
            m = RU_MONTHS.index(month_menu.get()) + 1
            return ddate(y, m, 1)

        nav = ctk.CTkFrame(win)
        nav.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        nav.grid_columnconfigure(1, weight=1)

        lbl = ctk.CTkLabel(nav, text="")
        lbl.grid(row=0, column=1)

        def prev_m():
            md = get_month_date()
            prev_last = md - timedelta(days=1)
            year_menu.set(str(prev_last.year))
            month_menu.set(RU_MONTHS[prev_last.month - 1])
            build_grid()

        def next_m():
            md = get_month_date()
            y, m = md.year, md.month
            if m == 12:
                y, m = y + 1, 1
            else:
                m += 1
            year_menu.set(str(y))
            month_menu.set(RU_MONTHS[m - 1])
            build_grid()

        ctk.CTkButton(nav, text="◀", width=60, command=prev_m).grid(row=0, column=0, padx=8, pady=6)
        ctk.CTkButton(nav, text="▶", width=60, command=next_m).grid(row=0, column=2, padx=8, pady=6)

        grid = ctk.CTkFrame(win)
        grid.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        for c in range(7):
            grid.grid_columnconfigure(c, weight=1)

        for i, w in enumerate(RU_WEEKDAY_SHORT):
            ctk.CTkLabel(grid, text=w).grid(row=0, column=i, pady=(4, 8))

        def pick(day: ddate):
            date_var.set(day.isoformat())
            try:
                win.destroy()
            except Exception:
                pass

        def build_grid():
            for child in grid.winfo_children():
                info = child.grid_info()
                if info and int(info.get("row", 0)) >= 1:
                    child.destroy()

            md = get_month_date()
            lbl.configure(text=f"{RU_MONTHS[md.month - 1]} {md.year}")

            start = md - timedelta(days=md.weekday())  # monday

            cur = start
            r = 1
            for _ in range(6):
                for c in range(7):
                    day = cur
                    btn = ctk.CTkButton(grid, text=str(day.day), height=34, command=lambda d=day: pick(d))
                    if day.month != md.month:
                        btn.configure(fg_color=("gray85", "gray20"))
                    if day == base:
                        btn.configure(border_width=2)
                    btn.grid(row=r, column=c, padx=3, pady=3, sticky="ew")
                    cur += timedelta(days=1)
                r += 1

        year_menu.configure(command=lambda _: build_grid())
        month_menu.configure(command=lambda _: build_grid())
        build_grid()