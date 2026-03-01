import customtkinter as ctk
from .todo_store import PersonalStore

from .calendar_tab import CalendarTab
from .notes_tab import NotesTab
from .tasks_tab import TasksTab


class TodoAppGUI(ctk.CTkFrame):
    def __init__(self, master, store: PersonalStore):
        super().__init__(master)

        self.store = store
        self.master = master

        self.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text="TODO", font=ctk.CTkFont(size=22, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=8, pady=(4, 10))

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        self.tab_calendar = self.tabs.add("Календарь")
        self.tab_notes    = self.tabs.add("Заметки")
        self.tab_tasks    = self.tabs.add("Задачи")
        self.tab_account  = self.tabs.add("Личный кабинет")

        # Подключаем вынесенные вкладки
        self.calendar_tab = CalendarTab(self.tab_calendar, self.store)
        self.notes_tab = NotesTab(self.tab_notes, self.store)
        self.tasks_tab = TasksTab(
    self.tab_tasks,
    self.store,
    on_changed=self.calendar_tab.refresh
)

        self._build_account()

    # --- управление из API ---
    def ui_show(self):
        try:
            self.master.deiconify()
            self.master.lift()
            self.master.focus_force()
        except Exception:
            pass

    def ui_open_tab(self, name: str):
        name = (name or "").strip().lower()
        mapping = {
            "calendar": "Календарь",
            "notes": "Заметки",
            "tasks": "Задачи",
            "account": "Личный кабинет",
        }
        tab = mapping.get(name)
        if tab:
            try:
                self.tabs.set(tab)
            except Exception:
                pass

    # --- Account (пока заглушка) ---
    def _build_account(self):
        self.tab_account.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(
            self.tab_account,
            text="Личный кабинет (MVP)\n\n"
                 "На этом этапе здесь будет:\n"
                 "• Вход / Создание аккаунта\n"
                 "• Список групп\n"
                 "• Создать группу / Подключиться\n"
                 "• Роли reader/editor\n\n"
                 "Сейчас вкладка-заготовка.",
            justify="left"
        )
        lbl.grid(row=0, column=0, sticky="w", padx=14, pady=14)