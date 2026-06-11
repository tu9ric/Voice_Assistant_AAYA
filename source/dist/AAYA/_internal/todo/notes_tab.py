import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


def _format_dt(s: str) -> str:
    try:
        return datetime.fromisoformat(s).strftime("%d-%m-%Y %H:%M")
    except Exception:
        return s


class NotesTab:
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store
        self.editing_note_id = None

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(self.parent)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(top, placeholder_text="Поиск по заметкам...")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(top, text="Найти", width=90, command=self.refresh).grid(row=0, column=1, padx=8, pady=8)
        ctk.CTkButton(top, text="Новая", width=90, command=self._reset_editor).grid(row=0, column=2, padx=8, pady=8)

        editor = ctk.CTkFrame(self.parent)
        editor.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        editor.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkEntry(editor, placeholder_text="Заголовок")
        self.title.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 6))

        self.body = ctk.CTkTextbox(editor, wrap="word", height=180)
        self.body.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        btns = ctk.CTkFrame(editor, fg_color="transparent")
        btns.grid(row=2, column=0, sticky="e", padx=8, pady=(0, 8))

        self.save_btn = ctk.CTkButton(btns, text="Сохранить", command=self._save_note)
        self.save_btn.pack(side="left", padx=4)

        self.clear_btn = ctk.CTkButton(btns, text="Очистить", command=self._reset_editor)
        self.clear_btn.pack(side="left", padx=4)

        self.list_wrap = ctk.CTkScrollableFrame(self.parent)
        self.list_wrap.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.list_wrap.grid_columnconfigure(0, weight=1)

        self.refresh()

    def _reset_editor(self):
        self.editing_note_id = None
        self.title.delete(0, "end")
        self.body.delete("1.0", "end")

    def _save_note(self):
        title = (self.title.get() or "").strip()
        body = (self.body.get("1.0", "end") or "").strip()

        try:
            if self.editing_note_id is None:
                self.store.create_note(title, body)
                messagebox.showinfo("TODO", "Заметка сохранена.")
            else:
                self.store.update_note(self.editing_note_id, title, body)
                messagebox.showinfo("TODO", "Заметка обновлена.")

            self._reset_editor()
            self.refresh()
        except Exception as e:
            messagebox.showerror("TODO", str(e))

    def _load_note_to_editor(self, note):
        self.editing_note_id = note.id
        self.title.delete(0, "end")
        self.title.insert(0, note.title or "")
        self.body.delete("1.0", "end")
        self.body.insert("1.0", note.body or "")

    def _delete_note(self, note_id: int):
        if not messagebox.askyesno("TODO", "Удалить заметку?"):
            return
        try:
            self.store.delete_note(note_id)
            if self.editing_note_id == note_id:
                self._reset_editor()
            self.refresh()
        except Exception as e:
            messagebox.showerror("TODO", str(e))

    def _duplicate_note(self, note):
        try:
            new_title = f"{note.title} (копия)"
            self.store.create_note(new_title, note.body)
            self.refresh()
        except Exception as e:
            messagebox.showerror("TODO", str(e))

    def refresh(self):
        query = (self.search_entry.get() or "").strip().lower()
        notes = self.store.list_notes()

        if query:
            notes = [
                n for n in notes
                if query in (n.title or "").lower() or query in (n.body or "").lower()
            ]

        for child in self.list_wrap.winfo_children():
            child.destroy()

        if not self.store.get_current_user():
            ctk.CTkLabel(
                self.list_wrap,
                text="Войдите в аккаунт, чтобы видеть и создавать свои заметки."
            ).grid(row=0, column=0, sticky="w", padx=8, pady=8)
            return

        if not notes:
            ctk.CTkLabel(self.list_wrap, text="Заметок пока нет.").grid(row=0, column=0, sticky="w", padx=8, pady=8)
            return

        for i, n in enumerate(notes):
            card = ctk.CTkFrame(self.list_wrap)
            card.grid(row=i, column=0, sticky="ew", padx=6, pady=6)
            card.grid_columnconfigure(0, weight=1)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
            top.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top,
                text=n.title or "Без названия",
                font=ctk.CTkFont(size=18, weight="bold")
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                top,
                text=_format_dt(n.created_at)
            ).grid(row=0, column=1, sticky="e", padx=(8, 0))

            preview = (n.body or "").strip()
            if len(preview) > 220:
                preview = preview[:220] + "..."

            ctk.CTkLabel(
                card,
                text=preview,
                justify="left",
                wraplength=900
            ).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 6))

            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.grid(row=2, column=0, sticky="e", padx=8, pady=(0, 8))

            ctk.CTkButton(btns, text="Открыть", width=90, command=lambda note=n: self._load_note_to_editor(note)).pack(side="left", padx=4)
            ctk.CTkButton(btns, text="Дублировать", width=110, command=lambda note=n: self._duplicate_note(note)).pack(side="left", padx=4)
            ctk.CTkButton(btns, text="Удалить", width=90, command=lambda note_id=n.id: self._delete_note(note_id)).pack(side="left", padx=4)