import customtkinter as ctk
from tkinter import messagebox

from .todo_store import PersonalStore
from .calendar.calendar_tab import CalendarTab
from .notes_tab import NotesTab
from .tasks_tab import TasksTab


class TodoAppGUI(ctk.CTkFrame):
    def __init__(self, master, store: PersonalStore):
        super().__init__(master)

        self.store = store
        self.master = master
        self._calendar_refresh_job = None

        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="TODO\nAAYA",
            font=ctk.CTkFont(size=28, weight="bold"),
            justify="left"
        ).grid(row=0, column=0, padx=20, pady=(24, 20), sticky="w")

        self.btn_calendar = ctk.CTkButton(self.sidebar, text="📅 Календарь", command=lambda: self.show_tab("calendar"))
        self.btn_calendar.grid(row=1, column=0, padx=16, pady=8, sticky="ew")

        self.btn_notes = ctk.CTkButton(self.sidebar, text="📝 Заметки", command=lambda: self.show_tab("notes"))
        self.btn_notes.grid(row=2, column=0, padx=16, pady=8, sticky="ew")

        self.btn_tasks = ctk.CTkButton(self.sidebar, text="✅ Задачи", command=lambda: self.show_tab("tasks"))
        self.btn_tasks.grid(row=3, column=0, padx=16, pady=8, sticky="ew")

        self.btn_account = ctk.CTkButton(self.sidebar, text="👤 Личный кабинет", command=lambda: self.show_tab("account"))
        self.btn_account.grid(row=4, column=0, padx=16, pady=8, sticky="ew")

        self.btn_group = ctk.CTkButton(self.sidebar, text="✨ Создать группу", command=self._on_create_group)
        self.btn_group.grid(row=6, column=0, padx=16, pady=16, sticky="ew")

        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkLabel(
            self.content,
            text="TODO",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        self.header.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.page = ctk.CTkFrame(self.content)
        self.page.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.page.grid_rowconfigure(0, weight=1)
        self.page.grid_columnconfigure(0, weight=1)

        self.tab_calendar = ctk.CTkFrame(self.page)
        self.tab_notes = ctk.CTkFrame(self.page)
        self.tab_tasks = ctk.CTkFrame(self.page)
        self.tab_account = ctk.CTkFrame(self.page)

        for tab in (self.tab_calendar, self.tab_notes, self.tab_tasks, self.tab_account):
            tab.grid(row=0, column=0, sticky="nsew")

        self.calendar_tab = CalendarTab(self.tab_calendar, self.store)
        self.notes_tab = NotesTab(self.tab_notes, self.store)
        self.tasks_tab = TasksTab(
            self.tab_tasks,
            self.store,
            on_changed=self.schedule_calendar_refresh
        )

        self._build_account()
        self.show_tab("calendar")
        self._refresh_account_view()
        self._refresh_all_user_views()

    def schedule_calendar_refresh(self):
        if self._calendar_refresh_job is not None:
            try:
                self.after_cancel(self._calendar_refresh_job)
            except Exception:
                pass
        self._calendar_refresh_job = self.after(180, self._run_calendar_refresh)

    def _run_calendar_refresh(self):
        self._calendar_refresh_job = None
        try:
            self.calendar_tab.refresh()
        except Exception:
            pass

    def _refresh_all_user_views(self):
        try:
            self.notes_tab.refresh()
        except Exception:
            pass
        try:
            self.tasks_tab.refresh()
        except Exception:
            pass
        try:
            self.calendar_tab.refresh()
        except Exception:
            pass

    def show_tab(self, name: str):
        mapping = {
            "calendar": (self.tab_calendar, "Календарь"),
            "notes": (self.tab_notes, "Заметки"),
            "tasks": (self.tab_tasks, "Задачи"),
            "account": (self.tab_account, "Личный кабинет"),
        }
        frame, title = mapping[name]
        frame.tkraise()
        self.header.configure(text=title)

    def ui_show(self):
        try:
            self.master.deiconify()
            self.master.lift()
            self.master.focus_force()
        except Exception:
            pass

    def ui_open_tab(self, name: str):
        name = (name or "").strip().lower()
        if name in {"calendar", "notes", "tasks", "account"}:
            self.show_tab(name)

    def _on_create_group(self):
        win = ctk.CTkToplevel(self.master)
        win.title("Создать группу")
        win.geometry("430x250")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Групповой режим",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(28, 10))

        ctk.CTkLabel(
            win,
            text="Кнопка уже готова.\nПозже сюда добавим создание группы,\nобщие задачи и общие заметки.",
            justify="center"
        ).pack(padx=20, pady=10)

        ctk.CTkButton(win, text="Закрыть", command=win.destroy).pack(pady=20)

    def _build_account(self):
        self.tab_account.grid_columnconfigure(0, weight=1)

        wrap = ctk.CTkFrame(self.tab_account)
        wrap.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        wrap.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            wrap,
            text="Личный кабинет",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 10))

        self.auth_wrap = ctk.CTkFrame(wrap, fg_color="transparent")
        self.auth_wrap.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.auth_wrap.grid_columnconfigure((0, 1), weight=1)

        login_box = ctk.CTkFrame(self.auth_wrap)
        login_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(login_box, text="Вход", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=16, pady=(16, 10))
        self.login_email = ctk.CTkEntry(login_box, placeholder_text="Email")
        self.login_email.pack(fill="x", padx=16, pady=8)
        self.login_password = ctk.CTkEntry(login_box, placeholder_text="Пароль", show="*")
        self.login_password.pack(fill="x", padx=16, pady=8)
        ctk.CTkButton(login_box, text="Войти", command=self._handle_login).pack(fill="x", padx=16, pady=(8, 16))

        reg_box = ctk.CTkFrame(self.auth_wrap)
        reg_box.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(reg_box, text="Регистрация", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=16, pady=(16, 10))
        self.reg_name = ctk.CTkEntry(reg_box, placeholder_text="Имя")
        self.reg_name.pack(fill="x", padx=16, pady=8)
        self.reg_email = ctk.CTkEntry(reg_box, placeholder_text="Email")
        self.reg_email.pack(fill="x", padx=16, pady=8)
        self.reg_password = ctk.CTkEntry(reg_box, placeholder_text="Пароль", show="*")
        self.reg_password.pack(fill="x", padx=16, pady=8)
        self.reg_password2 = ctk.CTkEntry(reg_box, placeholder_text="Повторите пароль", show="*")
        self.reg_password2.pack(fill="x", padx=16, pady=8)
        ctk.CTkButton(reg_box, text="Создать аккаунт", command=self._handle_register).pack(fill="x", padx=16, pady=(8, 16))

        self.profile_box = ctk.CTkFrame(wrap)
        self.profile_box.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.current_user_label = ctk.CTkLabel(
            self.profile_box,
            text="Текущий пользователь: не выполнен вход",
            font=ctk.CTkFont(size=16)
        )
        self.current_user_label.pack(anchor="w", padx=16, pady=(16, 8))

        self.current_user_email_label = ctk.CTkLabel(
            self.profile_box,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.current_user_email_label.pack(anchor="w", padx=16, pady=(0, 8))

        self.logout_btn = ctk.CTkButton(self.profile_box, text="Выйти", command=self._handle_logout)
        self.logout_btn.pack(anchor="w", padx=16, pady=(0, 16))

    def _refresh_account_view(self):
        user = self.store.get_current_user()
        if user:
            self.current_user_label.configure(text=f"Текущий пользователь: {user.name}")
            self.current_user_email_label.configure(text=f"Email: {user.email}")
            self.logout_btn.configure(state="normal")
            self.auth_wrap.grid_remove()
        else:
            self.current_user_label.configure(text="Текущий пользователь: не выполнен вход")
            self.current_user_email_label.configure(text="")
            self.logout_btn.configure(state="disabled")
            self.auth_wrap.grid()

    def _handle_register(self):
        name = (self.reg_name.get() or "").strip()
        email = (self.reg_email.get() or "").strip()
        pwd1 = self.reg_password.get() or ""
        pwd2 = self.reg_password2.get() or ""

        if pwd1 != pwd2:
            messagebox.showerror("TODO", "Пароли не совпадают.")
            return

        try:
            self.store.register_user(name, email, pwd1)
            messagebox.showinfo("TODO", "Аккаунт создан, вход выполнен.")
            self.reg_name.delete(0, "end")
            self.reg_email.delete(0, "end")
            self.reg_password.delete(0, "end")
            self.reg_password2.delete(0, "end")
            self._refresh_account_view()
            self._refresh_all_user_views()
        except Exception as e:
            messagebox.showerror("TODO", str(e))

    def _handle_login(self):
        email = (self.login_email.get() or "").strip()
        password = self.login_password.get() or ""

        try:
            self.store.login_user(email, password)
            messagebox.showinfo("TODO", "Вход выполнен.")
            self.login_email.delete(0, "end")
            self.login_password.delete(0, "end")
            self._refresh_account_view()
            self._refresh_all_user_views()
        except Exception as e:
            messagebox.showerror("TODO", str(e))

    def _handle_logout(self):
        try:
            self.store.logout_user()
            self._refresh_account_view()
            self._refresh_all_user_views()
            messagebox.showinfo("TODO", "Вы вышли из аккаунта.")
        except Exception as e:
            messagebox.showerror("TODO", str(e))