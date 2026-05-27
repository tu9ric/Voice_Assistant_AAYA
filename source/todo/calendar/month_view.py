import customtkinter as ctk

from datetime import date as ddate, timedelta

from .calendar_utils import RU_WEEKDAY_SHORT


class MonthView:

    def __init__(
        self,
        parent,
        store,
        selected_date,
        open_task_callback,
        open_day_callback
    ):

        self.parent = parent
        self.store = store
        self.selected_date = selected_date

        self.open_task_callback = open_task_callback
        self.open_day_callback = open_day_callback

        self.render()

    def render(self):

        root = ctk.CTkFrame(
            self.parent,
            corner_radius=18
        )

        root.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        canvas = ctk.CTkCanvas(
            root,
            bg="#242424",
            highlightthickness=0
        )

        canvas.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        canvas.update_idletasks()

        width = max(
            canvas.winfo_width(),
            1200
        )

        cols = 7
        rows = 6

        pad = 10

        cell_w = (width - pad * 2) / cols
        cell_h = 160

        # ================= WEEKDAYS =================

        for i, wd in enumerate(RU_WEEKDAY_SHORT):

            x = pad + i * cell_w

            canvas.create_text(
                x + cell_w / 2,
                24,
                text=wd.upper(),
                fill="#D1D5DB",
                font=("Arial", 12, "bold")
            )

        # ================= DAYS =================

        first = self.selected_date.replace(day=1)

        start = first - timedelta(days=first.weekday())

        cur = start

        for row in range(rows):

            for col in range(cols):

                day = cur

                x = pad + col * cell_w
                y = 40 + row * cell_h

                bg = "#2B2B2B"

                if day.month != first.month:
                    bg = "#262626"

                rect = canvas.create_rectangle(
                    x,
                    y,
                    x + cell_w - 6,
                    y + cell_h - 6,
                    fill=bg,
                    outline="#353535",
                    width=1
                )

                # ================= CLICK DAY =================

                canvas.tag_bind(
                    rect,
                    "<Button-1>",
                    lambda e, d=day:
                    self.open_day_callback(d)
                )

                # ================= DAY BADGE =================

                day_fill = "#2563EB"

                if day == ddate.today():
                    day_fill = "#3B82F6"

                badge = canvas.create_rectangle(
                    x + 10,
                    y + 10,
                    x + 80,
                    y + 34,
                    fill=day_fill,
                    outline=""
                )

                canvas.tag_bind(
                    badge,
                    "<Button-1>",
                    lambda e, d=day:
                    self.open_day_callback(d)
                )

                txt = canvas.create_text(
                    x + 45,
                    y + 22,
                    text=str(day.day),
                    fill="white",
                    font=("Arial", 12, "bold")
                )

                canvas.tag_bind(
                    txt,
                    "<Button-1>",
                    lambda e, d=day:
                    self.open_day_callback(d)
                )

                # ================= TASKS =================

                tasks = self.store.list_tasks(
                    date=day.isoformat(),
                    include_done=False
                )

                task_y = y + 48

                for t in tasks[:5]:

                    pill = canvas.create_rectangle(
                        x + 10,
                        task_y,
                        x + cell_w - 16,
                        task_y + 30,
                        fill="#2563EB",
                        outline="",
                        width=0
                    )

                    title = t.title

                    if len(title) > 24:
                        title = title[:24] + "..."

                    text = canvas.create_text(
                        x + 20,
                        task_y + 15,
                        text=title,
                        fill="white",
                        anchor="w",
                        font=("Arial", 11, "bold")
                    )

                    canvas.tag_bind(
                        pill,
                        "<Button-1>",
                        lambda e, task=t:
                        self.open_task_callback(task)
                    )

                    canvas.tag_bind(
                        text,
                        "<Button-1>",
                        lambda e, task=t:
                        self.open_task_callback(task)
                    )

                    task_y += 36

                cur += timedelta(days=1)