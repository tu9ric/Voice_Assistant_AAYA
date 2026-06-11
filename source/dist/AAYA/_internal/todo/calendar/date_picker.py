import customtkinter as ctk

from datetime import (
    date as ddate,
    timedelta
)


RU_WEEKDAY_SHORT = [
    "Пн",
    "Вт",
    "Ср",
    "Чт",
    "Пт",
    "Сб",
    "Вс"
]

RU_MONTHS = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь"
]


def open_date_picker(
    parent,
    selected_date,
    callback
):

    win = ctk.CTkToplevel(parent)

    win.title("Выбор даты")

    win.geometry("520x560")

    win.grab_set()
    win.lift()

    current = selected_date.replace(day=1)

    root = ctk.CTkFrame(win)

    root.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=12
    )

    # =====================================================
    # HEADER
    # =====================================================

    top = ctk.CTkFrame(root)

    top.pack(
        fill="x",
        pady=(0, 12)
    )

    title = ctk.CTkLabel(
        top,
        text="",
        font=ctk.CTkFont(
            size=28,
            weight="bold"
        )
    )

    title.pack(
        pady=(14, 10)
    )

    controls = ctk.CTkFrame(
        top,
        fg_color="transparent"
    )

    controls.pack(
        pady=(0, 12)
    )

    years = [
        str(y)
        for y in range(
            2000,
            2101
        )
    ]

    month_menu = ctk.CTkOptionMenu(
        controls,
        values=RU_MONTHS,
        width=170
    )

    month_menu.pack(
        side="left",
        padx=6
    )

    year_menu = ctk.CTkOptionMenu(
        controls,
        values=years,
        width=120
    )

    year_menu.pack(
        side="left",
        padx=6
    )

    btn_prev = ctk.CTkButton(
        controls,
        text="◀",
        width=42
    )

    btn_prev.pack(
        side="left",
        padx=(12, 4)
    )

    btn_next = ctk.CTkButton(
        controls,
        text="▶",
        width=42
    )

    btn_next.pack(
        side="left",
        padx=4
    )

    # =====================================================
    # CANVAS
    # =====================================================

    canvas = ctk.CTkCanvas(
        root,
        bg="#242424",
        highlightthickness=0
    )

    canvas.pack(
        fill="both",
        expand=True
    )

    cell_w = 64
    cell_h = 64

    # =====================================================
    # PICK
    # =====================================================

    def pick(day):

        callback(day)

        try:
            win.destroy()
        except Exception:
            pass

    # =====================================================
    # NAV
    # =====================================================

    def prev_month():

        nonlocal current

        prev = current - timedelta(days=1)

        current = prev.replace(day=1)

        render()

    def next_month():

        nonlocal current

        y = current.year
        m = current.month

        if m == 12:
            y += 1
            m = 1
        else:
            m += 1

        current = ddate(y, m, 1)

        render()

    btn_prev.configure(
        command=prev_month
    )

    btn_next.configure(
        command=next_month
    )

    # =====================================================
    # CHANGE MONTH/YEAR
    # =====================================================

    def on_change(_=None):

        nonlocal current

        y = int(year_menu.get())

        m = (
            RU_MONTHS.index(
                month_menu.get()
            ) + 1
        )

        current = ddate(y, m, 1)

        render()

    month_menu.configure(
        command=on_change
    )

    year_menu.configure(
        command=on_change
    )

    # =====================================================
    # RENDER
    # =====================================================

    def render():

        canvas.delete("all")

        title.configure(
            text=f"{RU_MONTHS[current.month - 1]} {current.year}"
        )

        month_menu.set(
            RU_MONTHS[current.month - 1]
        )

        year_menu.set(
            str(current.year)
        )

        start = current - timedelta(
            days=current.weekday()
        )

        # ================= WEEKDAYS =================

        for i, wd in enumerate(RU_WEEKDAY_SHORT):

            x = 28 + i * cell_w

            canvas.create_text(
                x + 22,
                20,
                text=wd,
                fill="#3B82F6",
                font=(
                    "Arial",
                    12,
                    "bold"
                )
            )

        # ================= DAYS =================

        cur = start

        for row in range(6):

            for col in range(7):

                day = cur

                x = 20 + col * cell_w
                y = 40 + row * cell_h

                fill = "#2E2E2E"

                if day == selected_date:

                    fill = "#2563EB"

                elif day.month != current.month:

                    fill = "#262626"

                rect = canvas.create_rectangle(
                    x,
                    y,
                    x + 54,
                    y + 54,
                    fill=fill,
                    outline="#353535",
                    width=1
                )

                txt_color = "white"

                if day.month != current.month:

                    txt_color = "#6B7280"

                txt = canvas.create_text(
                    x + 27,
                    y + 27,
                    text=str(day.day),
                    fill=txt_color,
                    font=(
                        "Arial",
                        13,
                        "bold"
                    )
                )

                canvas.tag_bind(
                    rect,
                    "<Button-1>",
                    lambda e, d=day:
                    pick(d)
                )

                canvas.tag_bind(
                    txt,
                    "<Button-1>",
                    lambda e, d=day:
                    pick(d)
                )

                cur += timedelta(days=1)

    render()