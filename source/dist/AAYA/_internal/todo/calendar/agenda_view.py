import customtkinter as ctk

from datetime import timedelta
from .task_details import TaskDetailsWindow
from .calendar_utils import (
    RU_WEEKDAY_SHORT,
    minutes
)


class AgendaView:

    def __init__(
        self,
        parent,
        store,
        selected_date,
        days_count,
        on_refresh=None
    ):

        self.parent = parent
        self.store = store
        self.selected_date = selected_date
        self.days_count = days_count
        self.on_refresh = on_refresh

        self.hour_h = 80
        self.day_w = 260
        self.header_h = 70
        self.timebar_w = 70

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

        start_day = self.selected_date

        if self.days_count > 1:

            start_day = self.selected_date - timedelta(
                days=self.selected_date.weekday()
            )

        days = [
            start_day + timedelta(days=i)
            for i in range(self.days_count)
        ]

        content_w = (
            self.timebar_w +
            len(days) * self.day_w
        )

        visible_w = root.winfo_screenwidth() - 220

        if len(days) <= 3:

            offset_x = max(
                0,
                (visible_w - content_w) // 2
            )

        else:

            offset_x = 0

        total_w = content_w + offset_x

        total_h = 40 + 24 * self.hour_h

        header_canvas = ctk.CTkCanvas(
            root,
            height=self.header_h,
            bg="#2B2B2B",
            highlightthickness=0
        )

        header_canvas.pack(
            fill="x",
            padx=8,
            pady=(8, 0)
        )

        header_canvas.configure(
            scrollregion=(
                0,
                0,
                total_w,
                self.header_h
            )
        )

        for i, day in enumerate(days):

            x = (
                offset_x +
                self.timebar_w +
                i * self.day_w
            )

            header_canvas.create_rectangle(
                x + 4,
                6,
                x + self.day_w - 4,
                62,
                outline="#353535",
                width=1,
                fill="#323232"
            )

            header_canvas.create_text(
                x + self.day_w / 2,
                24,
                text=RU_WEEKDAY_SHORT[
                    day.weekday()
                ].upper(),
                fill="#3B82F6",
                font=("Arial", 12, "bold")
            )

            header_canvas.create_text(
                x + self.day_w / 2,
                46,
                text=day.strftime("%d.%m"),
                fill="white",
                font=("Arial", 18, "bold")
            )

        body = ctk.CTkFrame(
            root
        )

        body.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        canvas = ctk.CTkCanvas(
            body,
            bg="#242424",
            highlightthickness=0
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ctk.CTkScrollbar(
            body,
            orientation="vertical",
            command=canvas.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.configure(
            scrollregion=(
                0,
                0,
                total_w,
                total_h
            )
        )

        for hour in range(24):

            y = 40 + hour * self.hour_h

            canvas.create_text(
                offset_x + 35,
                y + 12,
                text=f"{hour:02d}:00",
                fill="#8A8A8A",
                font=("Arial", 11)
            )

            canvas.create_line(
                offset_x + self.timebar_w,
                y,
                total_w,
                y,
                fill="#353535"
            )

        for i in range(len(days) + 1):

            x = (
                offset_x +
                self.timebar_w +
                i * self.day_w
            )

            canvas.create_line(
                x,
                40,
                x,
                total_h,
                fill="#353535"
            )

        for day_index, day in enumerate(days):

            tasks = self.store.list_tasks(
                date=day.isoformat(),
                include_done=False
            )

            for t in tasks:

                ts = getattr(
                    t,
                    "time_start",
                    None
                )

                te = getattr(
                    t,
                    "time_end",
                    None
                )

                if ts:

                    try:
                        start_min = minutes(ts)
                    except Exception:
                        start_min = 0

                else:

                    start_min = 0

                if te:

                    try:
                        end_min = minutes(te)
                    except Exception:
                        end_min = start_min + 60

                else:

                    end_min = start_min + 60

                duration = max(
                    30,
                    end_min - start_min
                )

                y = int(
                    40 +
                    (start_min / 60) * self.hour_h
                )

                h = int(
                    (duration / 60) * self.hour_h
                )

                h = max(
                    48,
                    h
                )

                x = (
                    offset_x +
                    self.timebar_w +
                    day_index * self.day_w +
                    8
                )

                w = self.day_w - 16

                card = ctk.CTkFrame(
                    canvas,
                    fg_color="#2563EB",
                    corner_radius=16,
                    width=w,
                    height=h
                )

                card.pack_propagate(
                    False
                )

                title = (
                    f"{ts} {t.title}"
                    if ts
                    else t.title
                )

                if getattr(
                    t,
                    "tag",
                    None
                ):

                    title += f" [{t.tag}]"

                lbl = ctk.CTkLabel(
                    card,
                    text=title,
                    text_color="white",
                    anchor="nw",
                    justify="left",
                    wraplength=w - 24,
                    font=ctk.CTkFont(
                        size=13,
                        weight="bold"
                    )
                )

                lbl.pack(
                    fill="both",
                    expand=True,
                    padx=10,
                    pady=8
                )

                canvas.create_window(
                    x,
                    y + 2,
                    anchor="nw",
                    window=card,
                    width=w,
                    height=h
                )

                card.bind(
                    "<Button-1>",
                    lambda e, task=t:
                    self._open_task(task)
                )

                lbl.bind(
                    "<Button-1>",
                    lambda e, task=t:
                    self._open_task(task)
                )

    def _open_task(
        self,
        task
    ):

        TaskDetailsWindow(
            self.parent.winfo_toplevel(),
            task,
            self.store,
            self.on_refresh
        )