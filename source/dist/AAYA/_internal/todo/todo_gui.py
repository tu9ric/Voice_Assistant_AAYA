import customtkinter as ctk
from tkinter import messagebox

from .todo_store import PersonalStore
from .calendar.calendar_tab import CalendarTab
from .notes_tab import NotesTab
from .tasks.tasks_tab import TasksTab


class TodoAppGUI(ctk.CTkFrame):

    def __init__(
        self,
        master,
        store: PersonalStore
    ):

        super().__init__(
            master
        )

        self.store = store
        self.master = master
        self._calendar_refresh_job = None

        self.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        master.grid_rowconfigure(
            0,
            weight=1
        )

        master.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        self.grid_columnconfigure(
            1,
            weight=1
        )

        # =================================================
        # SIDEBAR
        # =================================================

        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsw"
        )

        self.sidebar.grid_propagate(
            False
        )

        self.sidebar.grid_rowconfigure(
            7,
            weight=1
        )

        ctk.CTkLabel(
            self.sidebar,
            text="TODO\nAAYA",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            justify="left"
        ).grid(
            row=0,
            column=0,
            padx=20,
            pady=(24, 20),
            sticky="w"
        )

        self.btn_calendar = ctk.CTkButton(
            self.sidebar,
            text="📅 Календарь",
            height=40,
            corner_radius=14,
            command=lambda:
            self.show_tab(
                "calendar"
            )
        )

        self.btn_calendar.grid(
            row=1,
            column=0,
            padx=16,
            pady=8,
            sticky="ew"
        )

        self.btn_notes = ctk.CTkButton(
            self.sidebar,
            text="📝 Заметки",
            height=40,
            corner_radius=14,
            command=lambda:
            self.show_tab(
                "notes"
            )
        )

        self.btn_notes.grid(
            row=2,
            column=0,
            padx=16,
            pady=8,
            sticky="ew"
        )

        self.btn_tasks = ctk.CTkButton(
            self.sidebar,
            text="✅ Задачи",
            height=40,
            corner_radius=14,
            command=lambda:
            self.show_tab(
                "tasks"
            )
        )

        self.btn_tasks.grid(
            row=3,
            column=0,
            padx=16,
            pady=8,
            sticky="ew"
        )

        self.btn_account = ctk.CTkButton(
            self.sidebar,
            text="👤 Личный кабинет",
            height=40,
            corner_radius=14,
            command=lambda:
            self.show_tab(
                "account"
            )
        )

        self.btn_account.grid(
            row=4,
            column=0,
            padx=16,
            pady=8,
            sticky="ew"
        )

        self.btn_group = ctk.CTkButton(
            self.sidebar,
            text="✨ Создать группу",
            height=40,
            corner_radius=14,
            command=self._on_create_group
        )

        self.btn_group.grid(
            row=6,
            column=0,
            padx=16,
            pady=16,
            sticky="ew"
        )

        # =================================================
        # CONTENT
        # =================================================

        self.content = ctk.CTkFrame(
            self
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=16,
            pady=16
        )

        self.content.grid_rowconfigure(
            1,
            weight=1
        )

        self.content.grid_columnconfigure(
            0,
            weight=1
        )

        self.header = ctk.CTkLabel(
            self.content,
            text="TODO",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(16, 8)
        )

        self.page = ctk.CTkFrame(
            self.content
        )

        self.page.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

        self.page.grid_rowconfigure(
            0,
            weight=1
        )

        self.page.grid_columnconfigure(
            0,
            weight=1
        )

        self.tab_calendar = ctk.CTkFrame(
            self.page
        )

        self.tab_notes = ctk.CTkFrame(
            self.page
        )

        self.tab_tasks = ctk.CTkFrame(
            self.page
        )

        self.tab_account = ctk.CTkFrame(
            self.page
        )

        for tab in (
            self.tab_calendar,
            self.tab_notes,
            self.tab_tasks,
            self.tab_account
        ):

            tab.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

        # =================================================
        # ВАЖНО:
        # сначала notes/tasks, потом calendar.
        # =================================================

        self.notes_tab = NotesTab(
            self.tab_notes,
            self.store
        )

        self.tasks_tab = TasksTab(
            self.tab_tasks,
            self.store,
            on_changed=self.schedule_calendar_refresh
        )

        self.calendar_tab = CalendarTab(
            self.tab_calendar,
            self.store,
            on_tasks_changed=self.tasks_tab.refresh
        )

        self._build_account()

        self.show_tab(
            "calendar"
        )

        self._refresh_account_view()
        self._refresh_all_user_views()

    # =====================================================
    # CALENDAR REFRESH
    # =====================================================

    def schedule_calendar_refresh(
        self
    ):

        if self._calendar_refresh_job is not None:

            try:

                self.after_cancel(
                    self._calendar_refresh_job
                )

            except Exception:
                pass

        self._calendar_refresh_job = self.after(
            180,
            self._run_calendar_refresh
        )

    def _run_calendar_refresh(
        self
    ):

        self._calendar_refresh_job = None

        try:

            self.calendar_tab.refresh()

        except Exception as e:

            print(
                e
            )

    def _refresh_all_user_views(
        self
    ):

        try:

            self.notes_tab.refresh()

        except Exception as e:

            print(
                e
            )

        try:

            self.tasks_tab.refresh()

        except Exception as e:

            print(
                e
            )

        try:

            self.calendar_tab.refresh()

        except Exception as e:

            print(
                e
            )

    # =====================================================
    # SHOW TAB
    # =====================================================

    def show_tab(
        self,
        name: str
    ):

        mapping = {
            "calendar": (
                self.tab_calendar,
                "Календарь"
            ),
            "notes": (
                self.tab_notes,
                "Заметки"
            ),
            "tasks": (
                self.tab_tasks,
                "Задачи"
            ),
            "account": (
                self.tab_account,
                "Личный кабинет"
            ),
        }

        frame, title = mapping[
            name
        ]

        frame.tkraise()

        self.header.configure(
            text=title
        )

        if name == "calendar":

            try:

                self.calendar_tab.refresh()

            except Exception as e:

                print(
                    e
                )

        elif name == "tasks":

            try:

                self.tasks_tab.refresh()

            except Exception as e:

                print(
                    e
                )

        elif name == "notes":

            try:

                self.notes_tab.refresh()

            except Exception as e:

                print(
                    e
                )

        elif name == "account":

            try:

                self._refresh_account_view()

            except Exception as e:

                print(
                    e
                )

    # =====================================================
    # PUBLIC UI METHODS
    # =====================================================

    def ui_show(
        self
    ):

        try:

            self.master.deiconify()
            self.master.lift()
            self.master.focus_force()

        except Exception:
            pass

    def ui_open_tab(
        self,
        name: str
    ):

        name = (
            name
            or ""
        ).strip().lower()

        if name in {
            "calendar",
            "notes",
            "tasks",
            "account"
        }:

            self.show_tab(
                name
            )

    # =====================================================
    # GROUP PLACEHOLDER
    # =====================================================

    def _on_create_group(
        self
    ):

        win = ctk.CTkToplevel(
            self.master
        )

        win.title(
            "Создать группу"
        )

        win.geometry(
            "520x330"
        )

        win.resizable(
            False,
            False
        )

        try:

            win.transient(
                self.master.winfo_toplevel()
            )

            win.grab_set()
            win.lift()
            win.focus_force()

        except Exception:
            pass

        root = ctk.CTkFrame(
            win,
            corner_radius=20
        )

        root.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        ctk.CTkLabel(
            root,
            text="Групповой режим",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=22,
            pady=(24, 8)
        )

        ctk.CTkLabel(
            root,
            text=(
                "Кнопка уже готова.\n"
                "Позже сюда можно добавить создание группы,\n"
                "общие задачи, общие заметки и общий календарь."
            ),
            font=ctk.CTkFont(
                size=14
            ),
            text_color="#A8A8A8",
            justify="left",
            wraplength=430
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 20)
        )

        ctk.CTkButton(
            root,
            text="Закрыть",
            height=42,
            corner_radius=14,
            command=win.destroy
        ).pack(
            fill="x",
            padx=22,
            pady=(0, 22)
        )

    # =====================================================
    # ACCOUNT TAB
    # =====================================================

    def _build_account(
        self
    ):

        self.tab_account.grid_columnconfigure(
            0,
            weight=1
        )

        self.tab_account.grid_rowconfigure(
            0,
            weight=1
        )

        self.account_root = ctk.CTkFrame(
            self.tab_account,
            corner_radius=22
        )

        self.account_root.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=16
        )

        self.account_root.grid_columnconfigure(
            0,
            weight=1
        )

        self.account_root.grid_columnconfigure(
            1,
            weight=1
        )

        self.account_root.grid_rowconfigure(
            0,
            weight=1
        )

        # =================================================
        # LEFT PANEL
        # =================================================

        left_panel = ctk.CTkFrame(
            self.account_root,
            corner_radius=22
        )

        left_panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(18, 9),
            pady=18
        )

        left_panel.grid_columnconfigure(
            0,
            weight=1
        )

        left_panel.grid_rowconfigure(
            5,
            weight=1
        )

        ctk.CTkLabel(
            left_panel,
            text="Личный\nкабинет",
            font=ctk.CTkFont(
                size=38,
                weight="bold"
            ),
            justify="left"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=28,
            pady=(34, 10)
        )

        ctk.CTkLabel(
            left_panel,
            text=(
                "Войдите в аккаунт, чтобы задачи, календарь "
                "и заметки сохранялись отдельно для каждого пользователя."
            ),
            font=ctk.CTkFont(
                size=15
            ),
            text_color="#A8A8A8",
            justify="left",
            wraplength=390
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=28,
            pady=(0, 24)
        )

        info_box = ctk.CTkFrame(
            left_panel,
            corner_radius=18
        )

        info_box.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 16)
        )

        ctk.CTkLabel(
            info_box,
            text="Что даёт аккаунт?",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 8)
        )

        ctk.CTkLabel(
            info_box,
            text=(
                "• отдельные задачи для каждого пользователя\n"
                "• личные заметки\n"
                "• личный календарь\n"
                "• возможность позже подключить группы"
            ),
            font=ctk.CTkFont(
                size=14
            ),
            text_color="#A8A8A8",
            justify="left"
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 18)
        )

        self.account_status_box = ctk.CTkFrame(
            left_panel,
            corner_radius=18
        )

        self.account_status_box.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 16)
        )

        ctk.CTkLabel(
            self.account_status_box,
            text="Статус",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 4)
        )

        self.account_status_label = ctk.CTkLabel(
            self.account_status_box,
            text="Вход не выполнен",
            font=ctk.CTkFont(
                size=14
            ),
            text_color="#A8A8A8"
        )

        self.account_status_label.pack(
            anchor="w",
            padx=18,
            pady=(0, 16)
        )

        hint_box = ctk.CTkFrame(
            left_panel,
            corner_radius=18
        )

        hint_box.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 24)
        )

        ctk.CTkLabel(
            hint_box,
            text="Подсказка",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 4)
        )

        ctk.CTkLabel(
            hint_box,
            text=(
                "После регистрации вход выполняется автоматически. "
                "Все разделы TODO сразу обновятся под нового пользователя."
            ),
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8",
            justify="left",
            wraplength=360
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 16)
        )

        # =================================================
        # RIGHT PANEL
        # =================================================

        right_panel = ctk.CTkFrame(
            self.account_root,
            corner_radius=22
        )

        right_panel.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(9, 18),
            pady=18
        )

        right_panel.grid_columnconfigure(
            0,
            weight=1
        )

        right_panel.grid_rowconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            right_panel,
            text="Аккаунт TODO",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=24,
            pady=(26, 14)
        )

        # =================================================
        # AUTH CARD
        # =================================================

        self.auth_card = ctk.CTkFrame(
            right_panel,
            corner_radius=20
        )

        self.auth_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=24,
            pady=(0, 24)
        )

        self.auth_card.grid_columnconfigure(
            0,
            weight=1
        )

        self.auth_card.grid_rowconfigure(
            2,
            weight=1
        )

        self.auth_mode = "login"

        self.auth_switch = ctk.CTkSegmentedButton(
            self.auth_card,
            values=[
                "Вход",
                "Регистрация"
            ],
            command=self._set_auth_mode
        )

        self.auth_switch.set(
            "Вход"
        )

        self.auth_switch.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=22,
            pady=(22, 14)
        )

        self.auth_title = ctk.CTkLabel(
            self.auth_card,
            text="Вход в аккаунт",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        self.auth_title.grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 12)
        )

        self.forms_holder = ctk.CTkFrame(
            self.auth_card,
            fg_color="transparent"
        )

        self.forms_holder.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=22,
            pady=(0, 22)
        )

        self.forms_holder.grid_columnconfigure(
            0,
            weight=1
        )

        self.forms_holder.grid_rowconfigure(
            0,
            weight=1
        )

        self.login_form = ctk.CTkFrame(
            self.forms_holder,
            fg_color="transparent"
        )

        self.register_form = ctk.CTkFrame(
            self.forms_holder,
            fg_color="transparent"
        )

        for form in (
            self.login_form,
            self.register_form
        ):

            form.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            form.grid_columnconfigure(
                0,
                weight=1
            )

        # ================= LOGIN FORM =================

        ctk.CTkLabel(
            self.login_form,
            text="Email",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.login_email = ctk.CTkEntry(
            self.login_form,
            height=44,
            corner_radius=14,
            placeholder_text="example@mail.com"
        )

        self.login_email.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 14)
        )

        ctk.CTkLabel(
            self.login_form,
            text="Пароль",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.login_password = ctk.CTkEntry(
            self.login_form,
            height=44,
            corner_radius=14,
            placeholder_text="Введите пароль",
            show="*"
        )

        self.login_password.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        self.login_error_label = ctk.CTkLabel(
            self.login_form,
            text="",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#FF7777",
            justify="left",
            wraplength=420
        )

        self.login_error_label.grid(
            row=4,
            column=0,
            sticky="w",
            pady=(0, 10)
        )

        ctk.CTkButton(
            self.login_form,
            text="Войти",
            height=44,
            corner_radius=14,
            command=self._handle_login
        ).grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(0, 10)
        )

        ctk.CTkButton(
            self.login_form,
            text="Создать новый аккаунт",
            height=40,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=lambda:
            self._set_auth_mode(
                "Регистрация"
            )
        ).grid(
            row=6,
            column=0,
            sticky="ew"
        )

        # ================= REGISTER FORM =================

        ctk.CTkLabel(
            self.register_form,
            text="Имя",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.reg_name = ctk.CTkEntry(
            self.register_form,
            height=44,
            corner_radius=14,
            placeholder_text="Ваше имя"
        )

        self.reg_name.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            self.register_form,
            text="Email",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.reg_email = ctk.CTkEntry(
            self.register_form,
            height=44,
            corner_radius=14,
            placeholder_text="example@mail.com"
        )

        self.reg_email.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            self.register_form,
            text="Пароль",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.reg_password = ctk.CTkEntry(
            self.register_form,
            height=44,
            corner_radius=14,
            placeholder_text="Минимум 4 символа",
            show="*"
        )

        self.reg_password.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            self.register_form,
            text="Повторите пароль",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.reg_password2 = ctk.CTkEntry(
            self.register_form,
            height=44,
            corner_radius=14,
            placeholder_text="Повторите пароль",
            show="*"
        )

        self.reg_password2.grid(
            row=7,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        self.register_error_label = ctk.CTkLabel(
            self.register_form,
            text="",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#FF7777",
            justify="left",
            wraplength=420
        )

        self.register_error_label.grid(
            row=8,
            column=0,
            sticky="w",
            pady=(0, 10)
        )

        ctk.CTkButton(
            self.register_form,
            text="Создать аккаунт",
            height=44,
            corner_radius=14,
            command=self._handle_register
        ).grid(
            row=9,
            column=0,
            sticky="ew",
            pady=(0, 10)
        )

        ctk.CTkButton(
            self.register_form,
            text="Уже есть аккаунт",
            height=40,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=lambda:
            self._set_auth_mode(
                "Вход"
            )
        ).grid(
            row=10,
            column=0,
            sticky="ew"
        )

        # =================================================
        # PROFILE CARD
        # =================================================

        self.profile_card = ctk.CTkFrame(
            right_panel,
            corner_radius=20
        )

        self.profile_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=24,
            pady=(0, 24)
        )

        self.profile_card.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            self.profile_card,
            text="Профиль",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=24,
            pady=(28, 8)
        )

        self.profile_name_label = ctk.CTkLabel(
            self.profile_card,
            text="",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        self.profile_name_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=24,
            pady=(12, 4)
        )

        self.profile_email_label = ctk.CTkLabel(
            self.profile_card,
            text="",
            font=ctk.CTkFont(
                size=15
            ),
            text_color="#A8A8A8"
        )

        self.profile_email_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=24,
            pady=(0, 20)
        )

        profile_info = ctk.CTkFrame(
            self.profile_card,
            corner_radius=18
        )

        profile_info.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 20)
        )

        ctk.CTkLabel(
            profile_info,
            text="Данные пользователя активны",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 6)
        )

        ctk.CTkLabel(
            profile_info,
            text=(
                "Сейчас задачи, заметки и календарь отображаются "
                "для текущего аккаунта."
            ),
            font=ctk.CTkFont(
                size=14
            ),
            text_color="#A8A8A8",
            justify="left",
            wraplength=420
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 18)
        )

        ctk.CTkButton(
            self.profile_card,
            text="📅 Открыть календарь",
            height=42,
            corner_radius=14,
            command=lambda:
            self.show_tab(
                "calendar"
            )
        ).grid(
            row=4,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 10)
        )

        ctk.CTkButton(
            self.profile_card,
            text="✅ Открыть задачи",
            height=42,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=lambda:
            self.show_tab(
                "tasks"
            )
        ).grid(
            row=5,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 10)
        )

        ctk.CTkButton(
            self.profile_card,
            text="Выйти из аккаунта",
            height=42,
            corner_radius=14,
            fg_color="#8B0000",
            hover_color="#5E0000",
            command=self._handle_logout
        ).grid(
            row=6,
            column=0,
            sticky="ew",
            padx=24,
            pady=(10, 24)
        )

        self._set_auth_mode(
            "Вход"
        )

    def _set_auth_mode(
        self,
        value
    ):

        if value == "Регистрация":

            self.auth_mode = "register"

            try:

                self.auth_switch.set(
                    "Регистрация"
                )

            except Exception:
                pass

            self.auth_title.configure(
                text="Создание аккаунта"
            )

            self.register_form.tkraise()

            try:

                self.reg_name.focus()

            except Exception:
                pass

        else:

            self.auth_mode = "login"

            try:

                self.auth_switch.set(
                    "Вход"
                )

            except Exception:
                pass

            self.auth_title.configure(
                text="Вход в аккаунт"
            )

            self.login_form.tkraise()

            try:

                self.login_email.focus()

            except Exception:
                pass

        self.login_error_label.configure(
            text=""
        )

        self.register_error_label.configure(
            text=""
        )

    def _refresh_account_view(
        self
    ):

        user = self.store.get_current_user()

        if user:

            self.auth_card.grid_remove()
            self.profile_card.grid()

            self.profile_name_label.configure(
                text=user.name
            )

            self.profile_email_label.configure(
                text=f"Email: {user.email}"
            )

            self.account_status_label.configure(
                text=f"Выполнен вход: {user.name}",
                text_color="#7CFF95"
            )

        else:

            self.profile_card.grid_remove()
            self.auth_card.grid()

            self.account_status_label.configure(
                text="Вход не выполнен",
                text_color="#A8A8A8"
            )

            self._set_auth_mode(
                "Вход"
            )

    # =====================================================
    # AUTH HELPERS
    # =====================================================

    def _validate_email(
        self,
        email: str
    ) -> bool:

        email = (
            email
            or ""
        ).strip()

        return (
            "@" in email
            and "." in email
            and len(
                email
            ) >= 5
        )

    def _clear_auth_fields(
        self
    ):

        for entry in (
            self.login_email,
            self.login_password,
            self.reg_name,
            self.reg_email,
            self.reg_password,
            self.reg_password2
        ):

            try:

                entry.delete(
                    0,
                    "end"
                )

            except Exception:
                pass

        self.login_error_label.configure(
            text=""
        )

        self.register_error_label.configure(
            text=""
        )

    # =====================================================
    # AUTH ACTIONS
    # =====================================================

    def _handle_register(
        self
    ):

        name = (
            self.reg_name.get()
            or ""
        ).strip()

        email = (
            self.reg_email.get()
            or ""
        ).strip()

        pwd1 = self.reg_password.get() or ""
        pwd2 = self.reg_password2.get() or ""

        self.register_error_label.configure(
            text=""
        )

        if not name:

            self.register_error_label.configure(
                text="Введите имя."
            )

            return

        if not self._validate_email(
            email
        ):

            self.register_error_label.configure(
                text="Введите корректный email."
            )

            return

        if len(
            pwd1
        ) < 4:

            self.register_error_label.configure(
                text="Пароль должен содержать минимум 4 символа."
            )

            return

        if pwd1 != pwd2:

            self.register_error_label.configure(
                text="Пароли не совпадают."
            )

            return

        try:

            self.store.register_user(
                name,
                email,
                pwd1
            )

            self._clear_auth_fields()
            self._refresh_account_view()
            self._refresh_all_user_views()

            messagebox.showinfo(
                "TODO",
                "Аккаунт создан, вход выполнен."
            )

        except Exception as e:

            self.register_error_label.configure(
                text=str(
                    e
                )
            )

    def _handle_login(
        self
    ):

        email = (
            self.login_email.get()
            or ""
        ).strip()

        password = self.login_password.get() or ""

        self.login_error_label.configure(
            text=""
        )

        if not self._validate_email(
            email
        ):

            self.login_error_label.configure(
                text="Введите корректный email."
            )

            return

        if not password:

            self.login_error_label.configure(
                text="Введите пароль."
            )

            return

        try:

            self.store.login_user(
                email,
                password
            )

            self._clear_auth_fields()
            self._refresh_account_view()
            self._refresh_all_user_views()

            messagebox.showinfo(
                "TODO",
                "Вход выполнен."
            )

        except Exception as e:

            self.login_error_label.configure(
                text=str(
                    e
                )
            )

    def _handle_logout(
        self
    ):

        try:

            self.store.logout_user()

            self._refresh_account_view()
            self._refresh_all_user_views()

            messagebox.showinfo(
                "TODO",
                "Вы вышли из аккаунта."
            )

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )