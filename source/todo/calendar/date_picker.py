import customtkinter as ctk

from datetime import date as ddate, timedelta


RU_WEEKDAY_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

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


def open_date_picker(parent, selected_date, callback):

    win = ctk.CTkToplevel(parent)

    win.title("Выбор даты")
    win.geometry("420x470")

    win.grab_set()
    win.lift()

    current = selected_date.replace(day=1)

    root = ctk.CTkFrame(win)
    root.pack(fill="both", expand=True, padx=12, pady=12)

    # ================= HEADER =================

    header = ctk.CTkFrame(root)
    header.pack(fill="x", pady=(0, 10))

    month_label = ctk.CTkLabel(
        header,
        text="",
        font=ctk.CTkFont(size=22, weight="bold")
    )

    month_label.pack(side="top", pady=10)

    nav = ctk.CTkFrame(header, fg_color="transparent")
    nav.pack()

    # ================= GRID =================

    canvas = ctk.CTkCanvas(
        root,
        bg="#242424",
        highlightthickness=0
    )

    canvas.pack(fill="both", expand=True)

    cell_w = 54
    cell_h = 54

    def pick(day):

        callback(day)

        try:
            win.destroy()
        except Exception:
            pass

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

    ctk.CTkButton(
        nav,
        text="◀",
        width=50,
        command=prev_month
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        nav,
        text="▶",
        width=50,
        command=next_month
    ).pack(side="left", padx=6)

    def render():

        canvas.delete("all")

        month_label.configure(
            text=f"{RU_MONTHS[current.month - 1]} {current.year}"
        )

        start = current - timedelta(days=current.weekday())

        # weekdays

        for i, wd in enumerate(RU_WEEKDAY_SHORT):

            x = 20 + i * cell_w

            canvas.create_text(
                x + 20,
                20,
                text=wd,
                fill="#3B82F6",
                font=("Arial", 11, "bold")
            )

        cur = start

        for row in range(6):

            for col in range(7):

                x = 12 + col * cell_w
                y = 40 + row * cell_h

                fill = "#2E2E2E"

                if cur == selected_date:
                    fill = "#2563EB"

                elif cur.month != current.month:
                    fill = "#262626"

                canvas.create_rectangle(
                    x,
                    y,
                    x + 46,
                    y + 46,
                    fill=fill,
                    outline="#353535",
                    width=1
                )

                txt_color = "white"

                if cur.month != current.month:
                    txt_color = "#6B7280"

                canvas.create_text(
                    x + 23,
                    y + 23,
                    text=str(cur.day),
                    fill=txt_color,
                    font=("Arial", 12, "bold")
                )

                rect = canvas.create_rectangle(
                    x,
                    y,
                    x + 46,
                    y + 46,
                    outline="",
                    fill=""
                )

                canvas.tag_bind(
                    rect,
                    "<Button-1>",
                    lambda e, d=cur: pick(d)
                )

                cur += timedelta(days=1)

    render()