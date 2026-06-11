import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


# =====================================================
# HELPERS
# =====================================================

def _format_dt(
    s: str
) -> str:

    try:

        return datetime.fromisoformat(
            s
        ).strftime(
            "%d.%m.%Y %H:%M"
        )

    except Exception:

        return s or ""


def _short_text(
    text: str,
    limit: int = 120
) -> str:

    text = (
        text or ""
    ).strip()

    text = " ".join(
        text.split()
    )

    if len(
        text
    ) > limit:

        return text[:limit].strip() + "..."

    return text


# =====================================================
# NOTES TAB
# =====================================================

class NotesTab:

    def __init__(
        self,
        parent,
        store
    ):

        self.parent = parent
        self.store = store

        self.editing_note_id = None
        self.selected_note_id = None
        self.current_notes = []

        self._search_after_id = None
        self._is_dirty = False

        self.parent.grid_columnconfigure(
            0,
            weight=1
        )

        self.parent.grid_rowconfigure(
            0,
            weight=1
        )

        self._build_ui()
        self.refresh()

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(
        self
    ):

        self.root_frame = ctk.CTkFrame(
            self.parent,
            corner_radius=22
        )

        self.root_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=16
        )

        self.root_frame.grid_columnconfigure(
            0,
            weight=0
        )

        self.root_frame.grid_columnconfigure(
            1,
            weight=1
        )

        self.root_frame.grid_rowconfigure(
            1,
            weight=1
        )

        # =================================================
        # HEADER
        # =================================================

        header = ctk.CTkFrame(
            self.root_frame,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=18,
            pady=(18, 10)
        )

        header.grid_columnconfigure(
            0,
            weight=1
        )

        title_block = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        title_block.grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            title_block,
            text="Заметки",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            title_block,
            text="Быстрые записи, идеи и текстовые заметки",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        ).pack(
            anchor="w",
            pady=(2, 0)
        )

        header_buttons = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        header_buttons.grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.new_btn = ctk.CTkButton(
            header_buttons,
            text="➕ Новая",
            height=38,
            width=120,
            corner_radius=14,
            command=self._new_note
        )

        self.new_btn.pack(
            side="left",
            padx=(0, 8)
        )

        self.save_btn = ctk.CTkButton(
            header_buttons,
            text="💾 Сохранить",
            height=38,
            width=140,
            corner_radius=14,
            command=self._save_note
        )

        self.save_btn.pack(
            side="left",
            padx=(0, 8)
        )

        self.duplicate_btn = ctk.CTkButton(
            header_buttons,
            text="📄 Копия",
            height=38,
            width=110,
            corner_radius=14,
            command=self._duplicate_current_note
        )

        self.duplicate_btn.pack(
            side="left",
            padx=(0, 8)
        )

        self.delete_btn = ctk.CTkButton(
            header_buttons,
            text="🗑 Удалить",
            height=38,
            width=120,
            corner_radius=14,
            fg_color="#8B0000",
            hover_color="#5E0000",
            command=self._delete_current_note
        )

        self.delete_btn.pack(
            side="left"
        )

        # =================================================
        # LEFT PANEL
        # =================================================

        self.left_panel = ctk.CTkFrame(
            self.root_frame,
            width=340,
            corner_radius=18
        )

        self.left_panel.grid(
            row=1,
            column=0,
            sticky="ns",
            padx=(18, 10),
            pady=(0, 18)
        )

        self.left_panel.grid_propagate(
            False
        )

        self.left_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self.left_panel.grid_rowconfigure(
            3,
            weight=1
        )

        ctk.CTkLabel(
            self.left_panel,
            text="Мои заметки",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=14,
            pady=(14, 8)
        )

        self.search_entry = ctk.CTkEntry(
            self.left_panel,
            height=38,
            corner_radius=14,
            placeholder_text="Поиск по заметкам..."
        )

        self.search_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 8)
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self._on_search_change
        )

        self.notes_count_label = ctk.CTkLabel(
            self.left_panel,
            text="",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#A8A8A8"
        )

        self.notes_count_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=14,
            pady=(0, 8)
        )

        self.notes_list = ctk.CTkScrollableFrame(
            self.left_panel,
            corner_radius=14
        )

        self.notes_list.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        self.notes_list.grid_columnconfigure(
            0,
            weight=1
        )

        # =================================================
        # RIGHT PANEL
        # =================================================

        self.editor_panel = ctk.CTkFrame(
            self.root_frame,
            corner_radius=18
        )

        self.editor_panel.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(0, 18),
            pady=(0, 18)
        )

        self.editor_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self.editor_panel.grid_rowconfigure(
            3,
            weight=1
        )

        editor_top = ctk.CTkFrame(
            self.editor_panel,
            fg_color="transparent"
        )

        editor_top.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=16,
            pady=(16, 8)
        )

        editor_top.grid_columnconfigure(
            0,
            weight=1
        )

        self.editor_status = ctk.CTkLabel(
            editor_top,
            text="Новая заметка",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#7FD1FF"
        )

        self.editor_status.grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.note_date_label = ctk.CTkLabel(
            editor_top,
            text="",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#8E8E8E"
        )

        self.note_date_label.grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.title_entry = ctk.CTkEntry(
            self.editor_panel,
            height=46,
            corner_radius=14,
            placeholder_text="Заголовок заметки"
        )

        self.title_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 10)
        )

        self.title_entry.bind(
            "<KeyRelease>",
            self._mark_dirty
        )

        self.body_textbox = ctk.CTkTextbox(
            self.editor_panel,
            wrap="word",
            corner_radius=14,
            font=ctk.CTkFont(
                size=14
            )
        )

        self.body_textbox.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 10)
        )

        self.body_textbox.bind(
            "<KeyRelease>",
            self._mark_dirty
        )

        bottom_info = ctk.CTkFrame(
            self.editor_panel,
            fg_color="transparent"
        )

        bottom_info.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=16,
            pady=(0, 16)
        )

        bottom_info.grid_columnconfigure(
            0,
            weight=1
        )

        self.hint_label = ctk.CTkLabel(
            bottom_info,
            text="Ctrl + S — сохранить заметку",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#8E8E8E"
        )

        self.hint_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.stats_label = ctk.CTkLabel(
            bottom_info,
            text="0 символов",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#8E8E8E"
        )

        self.stats_label.grid(
            row=0,
            column=1,
            sticky="e"
        )

        # =================================================
        # SHORTCUTS
        # =================================================

        try:

            self.parent.bind_all(
                "<Control-s>",
                self._on_ctrl_s
            )

            self.parent.bind_all(
                "<Control-S>",
                self._on_ctrl_s
            )

        except Exception:
            pass

    # =====================================================
    # STATE
    # =====================================================

    def _mark_dirty(
        self,
        event=None
    ):

        self._is_dirty = True

        self._update_editor_status()
        self._update_stats()

    def _set_clean(
        self
    ):

        self._is_dirty = False

        self._update_editor_status()
        self._update_stats()

    def _update_editor_status(
        self
    ):

        if self.editing_note_id is None:

            base = "Новая заметка"

        else:

            base = f"Редактирование заметки #{self.editing_note_id}"

        if self._is_dirty:

            base += "  •  есть несохранённые изменения"

            color = "#FFD66B"

        else:

            color = "#7FD1FF"

        self.editor_status.configure(
            text=base,
            text_color=color
        )

    def _update_stats(
        self
    ):

        title = (
            self.title_entry.get()
            or ""
        ).strip()

        body = (
            self.body_textbox.get(
                "1.0",
                "end"
            )
            or ""
        ).strip()

        chars = len(
            body
        )

        words = len(
            body.split()
        )

        if title:

            shown_title = title

        else:

            shown_title = "Без заголовка"

        self.stats_label.configure(
            text=f"{words} слов · {chars} символов · {shown_title}"
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def _on_search_change(
        self,
        event=None
    ):

        if self._search_after_id:

            try:

                self.parent.after_cancel(
                    self._search_after_id
                )

            except Exception:
                pass

        self._search_after_id = self.parent.after(
            250,
            self.refresh
        )

    # =====================================================
    # EDITOR ACTIONS
    # =====================================================

    def _new_note(
        self
    ):

        if not self._confirm_discard_changes():
            return

        self.editing_note_id = None
        self.selected_note_id = None

        self.title_entry.delete(
            0,
            "end"
        )

        self.body_textbox.delete(
            "1.0",
            "end"
        )

        self.note_date_label.configure(
            text=""
        )

        self._set_clean()
        self._render_notes_list()
        self.title_entry.focus()

    def _reset_editor(
        self
    ):

        self._new_note()

    def _save_note(
        self
    ):

        title = (
            self.title_entry.get()
            or ""
        ).strip()

        body = (
            self.body_textbox.get(
                "1.0",
                "end"
            )
            or ""
        ).strip()

        if not body:

            messagebox.showwarning(
                "TODO",
                "Введите текст заметки."
            )

            return

        try:

            if self.editing_note_id is None:

                note = self.store.create_note(
                    title,
                    body
                )

                self.editing_note_id = note.id
                self.selected_note_id = note.id

                self.note_date_label.configure(
                    text=_format_dt(
                        note.created_at
                    )
                )

            else:

                self.store.update_note(
                    self.editing_note_id,
                    title,
                    body
                )

                self.selected_note_id = self.editing_note_id

            self._set_clean()
            self.refresh(
                keep_selection=True
            )

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )

    def _load_note_to_editor(
        self,
        note
    ):

        if not self._confirm_discard_changes():
            return

        self.editing_note_id = note.id
        self.selected_note_id = note.id

        self.title_entry.delete(
            0,
            "end"
        )

        self.title_entry.insert(
            0,
            note.title or ""
        )

        self.body_textbox.delete(
            "1.0",
            "end"
        )

        self.body_textbox.insert(
            "1.0",
            note.body or ""
        )

        self.note_date_label.configure(
            text=_format_dt(
                note.created_at
            )
        )

        self._set_clean()
        self._render_notes_list()

    def _delete_current_note(
        self
    ):

        if self.editing_note_id is None:

            self._new_note()
            return

        self._delete_note(
            self.editing_note_id
        )

    def _delete_note(
        self,
        note_id: int
    ):

        if not messagebox.askyesno(
            "TODO",
            "Удалить эту заметку?"
        ):

            return

        try:

            self.store.delete_note(
                note_id
            )

            if self.editing_note_id == note_id:

                self.editing_note_id = None
                self.selected_note_id = None

                self.title_entry.delete(
                    0,
                    "end"
                )

                self.body_textbox.delete(
                    "1.0",
                    "end"
                )

                self.note_date_label.configure(
                    text=""
                )

                self._set_clean()

            self.refresh()

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )

    def _duplicate_current_note(
        self
    ):

        if self.editing_note_id is None:

            title = (
                self.title_entry.get()
                or ""
            ).strip()

            body = (
                self.body_textbox.get(
                    "1.0",
                    "end"
                )
                or ""
            ).strip()

            if not body:

                messagebox.showwarning(
                    "TODO",
                    "Сначала введите текст заметки."
                )

                return

            try:

                note = self.store.create_note(
                    f"{title or 'Без названия'} (копия)",
                    body
                )

                self.refresh()

                self._load_note_to_editor(
                    note
                )

            except Exception as e:

                messagebox.showerror(
                    "TODO",
                    str(
                        e
                    )
                )

            return

        note = self._find_note_by_id(
            self.editing_note_id
        )

        if note:

            self._duplicate_note(
                note
            )

    def _duplicate_note(
        self,
        note
    ):

        try:

            new_title = (
                note.title
                or "Без названия"
            )

            copied = self.store.create_note(
                f"{new_title} (копия)",
                note.body or ""
            )

            self.refresh()

            self._load_note_to_editor(
                copied
            )

        except Exception as e:

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )

    def _confirm_discard_changes(
        self
    ) -> bool:

        if not self._is_dirty:
            return True

        return messagebox.askyesno(
            "TODO",
            "Есть несохранённые изменения. Продолжить без сохранения?"
        )

    def _on_ctrl_s(
        self,
        event=None
    ):

        self._save_note()

        return "break"

    # =====================================================
    # NOTES LIST
    # =====================================================

    def _find_note_by_id(
        self,
        note_id: int
    ):

        for note in self.current_notes:

            if note.id == note_id:

                return note

        try:

            for note in self.store.list_notes():

                if note.id == note_id:

                    return note

        except Exception:
            pass

        return None

    def refresh(
        self,
        keep_selection: bool = False
    ):

        if not self.store.get_current_user():

            self.current_notes = []

            self._render_notes_list()

            self.notes_count_label.configure(
                text="Войдите в аккаунт"
            )

            self._show_empty_state(
                "Войдите в аккаунт, чтобы создавать и просматривать заметки."
            )

            return

        query = (
            self.search_entry.get()
            or ""
        ).strip().lower()

        try:

            notes = self.store.list_notes()

        except Exception as e:

            notes = []

            messagebox.showerror(
                "TODO",
                str(
                    e
                )
            )

        if query:

            filtered = []

            for note in notes:

                title = (
                    note.title
                    or ""
                ).lower()

                body = (
                    note.body
                    or ""
                ).lower()

                if (
                    query in title
                    or query in body
                ):

                    filtered.append(
                        note
                    )

            notes = filtered

        self.current_notes = notes

        if not keep_selection and self.selected_note_id is None:

            if notes:

                self.selected_note_id = notes[0].id

        self._render_notes_list()

        self.notes_count_label.configure(
            text=f"Заметок: {len(notes)}"
        )

        if notes and self.editing_note_id is None and not self._is_dirty:

            first = self._find_note_by_id(
                self.selected_note_id
            ) or notes[0]

            self._load_note_to_editor_without_confirm(
                first
            )

        elif not notes and self.editing_note_id is None:

            self._show_empty_state(
                "Заметок пока нет. Создай первую заметку справа."
            )

    def _load_note_to_editor_without_confirm(
        self,
        note
    ):

        self.editing_note_id = note.id
        self.selected_note_id = note.id

        self.title_entry.delete(
            0,
            "end"
        )

        self.title_entry.insert(
            0,
            note.title or ""
        )

        self.body_textbox.delete(
            "1.0",
            "end"
        )

        self.body_textbox.insert(
            "1.0",
            note.body or ""
        )

        self.note_date_label.configure(
            text=_format_dt(
                note.created_at
            )
        )

        self._set_clean()

    def _show_empty_state(
        self,
        text: str
    ):

        self.editor_status.configure(
            text="Нет выбранной заметки",
            text_color="#A8A8A8"
        )

        self.note_date_label.configure(
            text=""
        )

        self.title_entry.delete(
            0,
            "end"
        )

        self.body_textbox.delete(
            "1.0",
            "end"
        )

        self.body_textbox.insert(
            "1.0",
            text
        )

        self._set_clean()

    def _render_notes_list(
        self
    ):

        for child in self.notes_list.winfo_children():

            child.destroy()

        if not self.store.get_current_user():

            ctk.CTkLabel(
                self.notes_list,
                text="Сначала войдите в аккаунт.",
                font=ctk.CTkFont(
                    size=14
                ),
                text_color="#A8A8A8",
                wraplength=260,
                justify="left"
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=10,
                pady=12
            )

            return

        if not self.current_notes:

            ctk.CTkLabel(
                self.notes_list,
                text="Заметок не найдено.",
                font=ctk.CTkFont(
                    size=14
                ),
                text_color="#A8A8A8"
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=10,
                pady=12
            )

            return

        for i, note in enumerate(
            self.current_notes
        ):

            self._add_note_card(
                i,
                note
            )

    def _add_note_card(
        self,
        row_index: int,
        note
    ):

        is_selected = (
            note.id == self.selected_note_id
        )

        card = ctk.CTkFrame(
            self.notes_list,
            corner_radius=14,
            fg_color=(
                "#1F6AA5"
                if is_selected
                else "#2B2B2B"
            )
        )

        card.grid(
            row=row_index,
            column=0,
            sticky="ew",
            padx=4,
            pady=5
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        title = note.title or "Без названия"

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            anchor="w",
            text_color="#FFFFFF"
        )

        title_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(10, 2)
        )

        date_label = ctk.CTkLabel(
            card,
            text=_format_dt(
                note.created_at
            ),
            font=ctk.CTkFont(
                size=11
            ),
            text_color=(
                "#D7EFFF"
                if is_selected
                else "#A8A8A8"
            ),
            anchor="w"
        )

        date_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 5)
        )

        preview = _short_text(
            note.body,
            120
        )

        if not preview:

            preview = "Пустая заметка"

        preview_label = ctk.CTkLabel(
            card,
            text=preview,
            font=ctk.CTkFont(
                size=12
            ),
            text_color=(
                "#EAF6FF"
                if is_selected
                else "#C8C8C8"
            ),
            justify="left",
            anchor="w",
            wraplength=270
        )

        preview_label.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 10)
        )

        # =================================================
        # CLICK HANDLERS
        # =================================================

        for widget in (
            card,
            title_label,
            date_label,
            preview_label
        ):

            widget.bind(
                "<Button-1>",
                lambda event, n=note:
                self._load_note_to_editor(
                    n
                )
            )

            widget.bind(
                "<Double-Button-1>",
                lambda event, n=note:
                self._load_note_to_editor(
                    n
                )
            )