import customtkinter as ctk
from datetime import date as ddate, datetime, timedelta


RU_WEEKDAY_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
RU_MONTHS = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]


def _parse_hm(s: str) -> tuple[int, int]:
    h, m = s.split(":")
    return int(h), int(m)


def _minutes(hm: str) -> int:
    h, m = _parse_hm(hm)
    return h * 60 + m


def _ui_date(d: ddate) -> str:
    return d.strftime("%d-%m-%Y")


class CalendarTab:
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)

        self.view = "Месяц"
        self.selected_date = ddate.today()

        top = ctk.CTkFrame(self.parent)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top.grid_columnconfigure(2, weight=1)

        self.view_menu = ctk.CTkOptionMenu(
            top,
            values=["Месяц", "Неделя", "3 дня", "День"],
            command=self._on_view_changed
        )
        self.view_menu.set(self.view)
        self.view_menu.grid(row=0, column=0, padx=8, pady=8, sticky="w")

        self.btn_prev = ctk.CTkButton(top, text="◀", width=55, command=self._prev)
        self.btn_prev.grid(row=0, column=1, padx=(0, 8), pady=8, sticky="w")

        self.lbl_date = ctk.CTkLabel(top, text=_ui_date(self.selected_date))
        self.lbl_date.grid(row=0, column=2, padx=8, pady=8, sticky="w")

        self.btn_next = ctk.CTkButton(top, text="▶", width=55, command=self._next)
        self.btn_next.grid(row=0, column=3, padx=(0, 8), pady=8, sticky="w")

        self.btn_pick = ctk.CTkButton(top, text="📅 Выбрать дату", width=160, command=self._open_date_picker)
        self.btn_pick.grid(row=0, column=4, padx=8, pady=8, sticky="e")

        self.content = ctk.CTkFrame(self.parent)
        self.content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self._rerender_scheduled = False
        self.refresh()

    def _on_view_changed(self, v: str):
        self.view = v
        self.refresh()

    def _prev(self):
        if self.view == "Месяц":
            first = self.selected_date.replace(day=1)
            prev_last = first - timedelta(days=1)
            self.selected_date = prev_last.replace(day=1)
        elif self.view == "Неделя":
            self.selected_date -= timedelta(days=7)
        elif self.view == "3 дня":
            self.selected_date -= timedelta(days=3)
        else:
            self.selected_date -= timedelta(days=1)
        self.refresh()

    def _next(self):
        if self.view == "Месяц":
            y, m = self.selected_date.year, self.selected_date.month
            if m == 12:
                y, m = y + 1, 1
            else:
                m += 1
            self.selected_date = ddate(y, m, 1)
        elif self.view == "Неделя":
            self.selected_date += timedelta(days=7)
        elif self.view == "3 дня":
            self.selected_date += timedelta(days=3)
        else:
            self.selected_date += timedelta(days=1)
        self.refresh()

    def _open_date_picker(self):
        win = ctk.CTkToplevel(self.parent.winfo_toplevel())
        win.title("Выбор даты")
        win.geometry("420x420")
        win.grab_set()

        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(2, weight=1)

        base = self.selected_date
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
            self.selected_date = day
            try:
                win.destroy()
            except Exception:
                pass
            self.refresh()

        def build_grid():
            for child in grid.winfo_children():
                info = child.grid_info()
                if info and int(info.get("row", 0)) >= 1:
                    child.destroy()

            md = get_month_date()
            lbl.configure(text=f"{RU_MONTHS[md.month - 1]} {md.year}")

            first = md
            start = first - timedelta(days=first.weekday())

            cur = start
            r = 1
            for _ in range(6):
                for c in range(7):
                    day = cur
                    btn = ctk.CTkButton(grid, text=str(day.day), height=34, command=lambda d=day: pick(d))
                    if day.month != md.month:
                        btn.configure(fg_color=("gray85", "gray20"))
                    if day == self.selected_date:
                        btn.configure(border_width=2)
                    btn.grid(row=r, column=c, padx=3, pady=3, sticky="ew")
                    cur += timedelta(days=1)
                r += 1

        year_menu.configure(command=lambda _: build_grid())
        month_menu.configure(command=lambda _: build_grid())
        build_grid()

    def refresh(self):
        self.lbl_date.configure(text=_ui_date(self.selected_date))

        for child in self.content.winfo_children():
            child.destroy()

        if self.view == "Месяц":
            self._render_month_view()
        else:
            days = 7 if self.view == "Неделя" else (3 if self.view == "3 дня" else 1)
            self._render_agenda_view(days)

    def _render_month_view(self):
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew")
        for c in range(7):
            frame.grid_columnconfigure(c, weight=1)
        for r in range(7):
            frame.grid_rowconfigure(r, weight=1)

        y, m = self.selected_date.year, self.selected_date.month
        first = ddate(y, m, 1)
        start = first - timedelta(days=first.weekday())

        for i, w in enumerate(RU_WEEKDAY_SHORT):
            ctk.CTkLabel(frame, text=w).grid(row=0, column=i, pady=(6, 6))

        cur = start
        row = 1
        for _ in range(6):
            for col in range(7):
                day = cur
                cell = ctk.CTkFrame(frame)
                cell.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
                cell.grid_columnconfigure(0, weight=1)
                cell.grid_rowconfigure(1, weight=1)

                title_btn = ctk.CTkButton(
                    cell, text=f"{day.day}", width=40, height=28,
                    command=lambda d=day: self._jump_to_day(d)
                )
                if day.month != m:
                    title_btn.configure(fg_color=("gray85", "gray20"))
                title_btn.grid(row=0, column=0, sticky="w", padx=6, pady=(6, 2))

                tasks = self.store.list_tasks(date=day.isoformat(), include_done=False)
                mini = ctk.CTkLabel(cell, text=self._mini_tasks(tasks), justify="left")
                mini.grid(row=1, column=0, sticky="nw", padx=6, pady=(0, 6))

                cur += timedelta(days=1)
            row += 1

    def _mini_tasks(self, tasks):
        if not tasks:
            return ""
        lines = []
        for t in tasks[:3]:
            if getattr(t, "time_start", None):
                lines.append(f"• {t.time_start} {t.title}")
            else:
                lines.append(f"• {t.title}")
        if len(tasks) > 3:
            lines.append(f"… +{len(tasks) - 3}")
        return "\n".join(lines)

    def _jump_to_day(self, day: ddate):
        self.selected_date = day
        self.view_menu.set("День")
        self.view = "День"
        self.refresh()

    def _render_agenda_view(self, days_count: int):
        wrapper = ctk.CTkFrame(self.content)
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        canvas = ctk.CTkCanvas(wrapper, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        scroll = ctk.CTkScrollbar(wrapper, orientation="vertical", command=canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scroll.set)

        inner = ctk.CTkFrame(canvas)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_config(_):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(inner_id, width=canvas.winfo_width())

        inner.bind("<Configure>", _on_config)

        hour_h = 56
        all_day_h = 28
        time_col_w = 70

        start_day = self.selected_date
        if days_count > 1:
            start_day = self.selected_date - timedelta(days=self.selected_date.weekday())

        day_list = [start_day + timedelta(days=i) for i in range(days_count)]

        header = ctk.CTkFrame(inner)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=0)
        for i in range(days_count):
            header.grid_columnconfigure(i + 1, weight=1)

        ctk.CTkLabel(header, text="").grid(row=0, column=0, padx=6, pady=6)

        for i, day in enumerate(day_list):
            wd = RU_WEEKDAY_SHORT[day.weekday()]
            ctk.CTkLabel(header, text=f"{wd} {day.strftime('%d-%m-%Y')}").grid(
                row=0, column=i + 1, padx=6, pady=6, sticky="w"
            )

        body_wrap = ctk.CTkFrame(inner)
        body_wrap.grid(row=1, column=0, sticky="nsew")
        body_wrap.grid_columnconfigure(1, weight=1)
        body_wrap.grid_rowconfigure(0, weight=1)

        time_col = ctk.CTkFrame(body_wrap, width=time_col_w)
        time_col.grid(row=0, column=0, sticky="ns")
        time_col.grid_propagate(False)

        days_container = ctk.CTkFrame(body_wrap)
        days_container.grid(row=0, column=1, sticky="nsew")
        days_container.grid_columnconfigure(0, weight=1)
        days_container.grid_rowconfigure(1, weight=1)

        all_day_row = ctk.CTkFrame(days_container, height=all_day_h)
        all_day_row.grid(row=0, column=0, sticky="ew")
        for i in range(days_count):
            all_day_row.grid_columnconfigure(i, weight=1)
        all_day_row.grid_propagate(False)

        days_grid = ctk.CTkFrame(days_container)
        days_grid.grid(row=1, column=0, sticky="nsew")
        for i in range(days_count):
            days_grid.grid_columnconfigure(i, weight=1)

        spacer = ctk.CTkLabel(time_col, text="", height=all_day_h)
        spacer.grid(row=0, column=0, sticky="ew")

        for hour in range(24):
            time_col.grid_rowconfigure(hour + 1, minsize=hour_h)
            ctk.CTkLabel(time_col, text=f"{hour:02d}:00").grid(
                row=hour + 1, column=0, padx=8, sticky="ne"
            )

        for i in range(days_count):
            cell = ctk.CTkFrame(all_day_row, height=all_day_h)
            cell.grid(row=0, column=i, sticky="nsew", padx=2, pady=1)
            cell.grid_propagate(False)

        for hour in range(24):
            days_grid.grid_rowconfigure(hour, minsize=hour_h)
            for i in range(days_count):
                cell = ctk.CTkFrame(days_grid)
                cell.grid(row=hour, column=i, sticky="nsew", padx=2, pady=1)
                cell.grid_propagate(False)

        overlay = ctk.CTkFrame(days_grid, fg_color="transparent")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        tasks_by_day = {d.isoformat(): self.store.list_tasks(date=d.isoformat(), include_done=True) for d in day_list}

        for i, day in enumerate(day_list):
            tasks = tasks_by_day[day.isoformat()]
            all_day = [t for t in tasks if not getattr(t, "time_start", None) and int(getattr(t, "done", 0)) == 0]
            if all_day:
                txt = " • ".join([t.title for t in all_day[:2]]) + ("…" if len(all_day) > 2 else "")
                badge = ctk.CTkLabel(all_day_row, text=txt)
                badge.grid(row=0, column=i, sticky="ew", padx=6, pady=2)

        days_grid.update_idletasks()
        total_w = max(days_grid.winfo_width(), days_container.winfo_width() - 4, 300)

        if total_w < 120 and not self._rerender_scheduled:
            self._rerender_scheduled = True
            self.parent.after(50, lambda: (setattr(self, "_rerender_scheduled", False), self.refresh()))
            return

        day_w = total_w / max(days_count, 1)

        for i, day in enumerate(day_list):
            tasks = tasks_by_day[day.isoformat()]
            for t in tasks:
                if int(getattr(t, "done", 0)) == 1:
                    continue

                ts = getattr(t, "time_start", None)
                if not ts:
                    continue

                try:
                    start_min = _minutes(ts)
                except Exception:
                    continue

                te = getattr(t, "time_end", None)
                if te:
                    try:
                        end_min = _minutes(te)
                    except Exception:
                        end_min = min(start_min + 60, 24 * 60)
                else:
                    end_min = min(start_min + 60, 24 * 60)

                y = (start_min / 60) * hour_h
                h = max(24, ((end_min - start_min) / 60) * hour_h)

                w = max(40, int(day_w - 12))
                hh = max(24, int(h))

                block = ctk.CTkFrame(overlay, width=w, height=hh)
                block.pack_propagate(False)

                title = f"{ts} {t.title}"
                if getattr(t, "tag", None):
                    title += f" [{t.tag}]"

                label = ctk.CTkLabel(block, text=title, justify="left", anchor="w")
                label.pack(fill="both", expand=True, padx=6, pady=4)

                block.place(
                    x=int(i * day_w + 6),
                    y=int(y + 2)
                )