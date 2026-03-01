import customtkinter as ctk
from tkinter import messagebox

class NotesTab:
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self.parent)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkEntry(top, placeholder_text="Заголовок (необязательно)")
        self.title.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        btn_add = ctk.CTkButton(top, text="➕ Сохранить заметку", command=self._save_note)
        btn_add.grid(row=0, column=1, padx=8, pady=8)

        self.body = ctk.CTkTextbox(self.parent, wrap="word")
        self.body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.list_box = ctk.CTkTextbox(self.parent, wrap="word", height=180)
        self.list_box.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.list_box.configure(state="disabled")

        self.refresh()

    def _save_note(self):
        title = (self.title.get() or "").strip()
        body = (self.body.get("1.0", "end") or "").strip()
        try:
            self.store.create_note(title, body)
            self.title.delete(0, "end")
            self.body.delete("1.0", "end")
            self.refresh()
            messagebox.showinfo("TODO", "Заметка сохранена (локально).")
        except Exception as e:
            messagebox.showerror("TODO", str(e))

    def refresh(self):
        notes = self.store.list_notes()
        self.list_box.configure(state="normal")
        self.list_box.delete("1.0", "end")
        if not notes:
            self.list_box.insert("end", "Заметок пока нет.\n")
        else:
            for n in notes[:20]:
                self.list_box.insert("end", f"#{n.id} [{n.created_at}] {n.title}\n")
        self.list_box.configure(state="disabled")