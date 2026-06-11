import io
import json
import os
import platform
import subprocess
import sys
import threading
import time
from contextlib import redirect_stdout
from dataclasses import dataclass
from typing import List, Set

import customtkinter as ctk
from tkinter import messagebox

import speech_recognition as sr

from core.processor import CommandProcessor
from core.tts import Speaker


HOTKEY = "ctrl+shift+space"


# =====================================================
# RESOURCE PATH
# =====================================================

def resource_path(
    relative_path: str
) -> str:

    if hasattr(
        sys,
        "_MEIPASS"
    ):

        return os.path.join(
            sys._MEIPASS,
            relative_path
        )

    return os.path.join(
        os.path.abspath("."),
        relative_path
    )


# =====================================================
# PLATFORM CONTEXT
# =====================================================

@dataclass(frozen=True)
class PlatformContext:

    os_name: str
    is_windows: bool
    is_linux: bool
    is_macos: bool


def detect_platform() -> PlatformContext:

    name = platform.system().lower()

    return PlatformContext(
        os_name=name,
        is_windows=(name == "windows"),
        is_linux=(name == "linux"),
        is_macos=(name == "darwin"),
    )


# =====================================================
# NOTIFIER
# =====================================================

class Notifier:

    def __init__(
        self,
        ctx: PlatformContext,
        app_id: str = "AAYA",
        root=None
    ):

        self.ctx = ctx
        self.app_id = app_id
        self.root = root
        self.tray = None

        self._last_toast_key = ""
        self._last_toast_time = 0.0

        self._windows_toasts_ok = False
        self._WindowsToaster = None
        self._Toast = None
        self._toaster = None

        self._winotify_ok = False
        self._Notification = None
        self._audio = None

        if ctx.is_windows:

            try:

                from windows_toasts import WindowsToaster, Toast

                self._WindowsToaster = WindowsToaster
                self._Toast = Toast

                self._toaster = WindowsToaster(
                    self.app_id
                )

                self._windows_toasts_ok = True

                print(
                    "Windows-уведомления: windows-toasts подключён"
                )

            except Exception as e:

                self._windows_toasts_ok = False

                print(
                    f"windows-toasts недоступен: {e}"
                )

            try:

                from winotify import Notification, audio

                self._Notification = Notification
                self._audio = audio
                self._winotify_ok = True

                print(
                    "Windows-уведомления: winotify подключён"
                )

            except Exception as e:

                self._winotify_ok = False

                print(
                    f"winotify недоступен: {e}"
                )

    def toast(
        self,
        title: str,
        msg: str
    ) -> None:

        title = (
            title or "AAYA"
        ).strip()

        msg = (
            msg or ""
        ).strip()

        if not msg:
            return

        # =================================================
        # ЗАЩИТА ОТ ДУБЛЕЙ
        # =================================================
        # Если одно и то же уведомление вызывается несколько
        # раз подряд меньше чем за 1.5 секунды — показываем
        # только первое.
        # =================================================

        now = time.time()
        key = f"{title}|{msg}"

        if (
            key == self._last_toast_key
            and now - self._last_toast_time < 1.5
        ):

            return

        self._last_toast_key = key
        self._last_toast_time = now

        # =================================================
        # Все уведомления отправляем в главный GUI-поток.
        # =================================================

        if self.root:

            try:

                self.root.after(
                    0,
                    lambda:
                    self._toast_main_thread(
                        title,
                        msg
                    )
                )

                return

            except Exception as e:

                print(
                    f"Ошибка передачи уведомления в GUI-поток: {e}"
                )

        self._toast_main_thread(
            title,
            msg
        )

    def _toast_main_thread(
        self,
        title: str,
        msg: str
    ) -> None:

        # =================================================
        # 1. WINDOWS-TOASTS
        # =================================================

        if self.ctx.is_windows and self._windows_toasts_ok:

            try:

                toast = self._Toast()

                toast.text_fields = [
                    title,
                    msg
                ]

                self._toaster.show_toast(
                    toast
                )

                return

            except Exception as e:

                print(
                    f"Ошибка windows-toasts уведомления: {e}"
                )

        # =================================================
        # 2. WINOTIFY FALLBACK
        # =================================================

        if self.ctx.is_windows and self._winotify_ok:

            try:

                n = self._Notification(
                    app_id=self.app_id,
                    title=title,
                    msg=msg,
                    duration="short"
                )

                try:

                    if self._audio:

                        n.set_audio(
                            self._audio.Default,
                            loop=False
                        )

                except Exception:
                    pass

                n.show()

                return

            except Exception as e:

                print(
                    f"Ошибка winotify уведомления: {e}"
                )

        # =================================================
        # 3. TRAY FALLBACK
        # =================================================

        tray = getattr(
            self,
            "tray",
            None
        )

        if tray:

            try:

                ok = tray.notify(
                    title,
                    msg
                )

                if ok:

                    return

            except Exception as e:

                print(
                    f"Ошибка уведомления через трей: {e}"
                )

        # =================================================
        # 4. LINUX FALLBACK
        # =================================================

        if self.ctx.is_linux:

            try:

                subprocess.run(
                    [
                        "notify-send",
                        title,
                        msg
                    ],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                return

            except Exception as e:

                print(
                    f"Ошибка Linux-уведомления: {e}"
                )

        # =================================================
        # 5. ВСТРОЕННОЕ УВЕДОМЛЕНИЕ
        # =================================================

        print(
            f"{title}: {msg}"
        )

        self._fallback_popup(
            title,
            msg
        )

    def _fallback_popup(
        self,
        title: str,
        msg: str
    ):

        if not self.root:
            return

        try:

            self._show_popup(
                title,
                msg
            )

        except Exception as e:

            print(
                f"Ошибка fallback-уведомления: {e}"
            )

    def _show_popup(
        self,
        title: str,
        msg: str
    ):

        popup = ctk.CTkToplevel(
            self.root
        )

        popup.title(
            title
        )

        popup.geometry(
            "370x130"
        )

        popup.resizable(
            False,
            False
        )

        popup.attributes(
            "-topmost",
            True
        )

        try:

            screen_w = popup.winfo_screenwidth()
            screen_h = popup.winfo_screenheight()

            x = screen_w - 400
            y = screen_h - 200

            popup.geometry(
                f"370x130+{x}+{y}"
            )

        except Exception:
            pass

        frame = ctk.CTkFrame(
            popup,
            corner_radius=16
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            anchor="w"
        ).pack(
            fill="x",
            padx=14,
            pady=(12, 4)
        )

        ctk.CTkLabel(
            frame,
            text=msg,
            wraplength=320,
            justify="left",
            anchor="w"
        ).pack(
            fill="x",
            padx=14,
            pady=(0, 10)
        )

        popup.after(
            3500,
            popup.destroy
        )

# =====================================================
# HOTKEYS
# =====================================================

class Hotkeys:

    def __init__(
        self
    ):

        self._keyboard = None

        try:

            import keyboard

            self._keyboard = keyboard

        except Exception:

            self._keyboard = None

    @property
    def available(
        self
    ) -> bool:

        return self._keyboard is not None

    def register(
        self,
        hotkey: str,
        callback
    ) -> bool:

        if not self._keyboard:
            return False

        try:

            self._keyboard.add_hotkey(
                hotkey,
                callback
            )

            return True

        except Exception:

            return False

    def unregister_all(
        self
    ) -> None:

        if not self._keyboard:
            return

        try:

            self._keyboard.unhook_all_hotkeys()

        except Exception:
            pass


# =====================================================
# HELPERS
# =====================================================

def _clean_output_lines(
    raw: str
) -> List[str]:

    lines = []

    for line in raw.splitlines():

        s = line.strip()

        if not s:
            continue

        low = s.lower()

        if low.startswith("[") and "]" in low:
            continue

        lines.append(
            s
        )

    return lines


def _final_answer_from_captured(
    raw: str
) -> str:

    lines = _clean_output_lines(
        raw
    )

    if not lines:
        return ""

    return lines[-1].strip()


# =====================================================
# TRAY
# =====================================================

class Tray:

    def __init__(
        self,
        app_name: str,
        open_cb,
        exit_cb
    ):

        self.app_name = app_name
        self._open_cb = open_cb
        self._exit_cb = exit_cb

        self._icon = None
        self._thread = None

        self.available = False
        self.started = False

    def start(
        self
    ) -> bool:

        try:

            import pystray
            from PIL import Image, ImageDraw

        except Exception as e:

            print(
                f"Трей недоступен: {e}"
            )

            self.available = False
            self.started = False

            return False

        try:

            img = Image.new(
                "RGBA",
                (
                    64,
                    64
                ),
                (
                    0,
                    0,
                    0,
                    0
                )
            )

            d = ImageDraw.Draw(
                img
            )

            d.rounded_rectangle(
                (
                    8,
                    8,
                    56,
                    56
                ),
                radius=14,
                outline=(
                    0,
                    180,
                    255,
                    255
                ),
                width=4
            )

            d.text(
                (
                    24,
                    18
                ),
                "A",
                fill=(
                    0,
                    180,
                    255,
                    255
                )
            )

            menu = pystray.Menu(
                pystray.MenuItem(
                    "Открыть AAYA",
                    lambda icon, item:
                    self._safe_open()
                ),
                pystray.MenuItem(
                    "Выход",
                    lambda icon, item:
                    self._safe_exit()
                ),
            )

            self._icon = pystray.Icon(
                self.app_name,
                img,
                self.app_name,
                menu
            )

            def _run():

                try:

                    self.available = True
                    self.started = True

                    self._icon.run()

                except Exception as e:

                    self.started = False

                    print(
                        f"Ошибка работы трея: {e}"
                    )

            self._thread = threading.Thread(
                target=_run,
                daemon=True
            )

            self._thread.start()

            self.available = True
            self.started = True

            return True

        except Exception as e:

            print(
                f"Не удалось запустить трей: {e}"
            )

            self.available = False
            self.started = False

            return False

    def _safe_open(
        self
    ):

        try:

            self._open_cb()

        except Exception as e:

            print(
                f"Ошибка открытия из трея: {e}"
            )

    def _safe_exit(
        self
    ):

        try:

            self._exit_cb()

        except Exception as e:

            print(
                f"Ошибка выхода из трея: {e}"
            )

    def notify(
        self,
        title: str,
        msg: str
    ) -> bool:

        if not self._icon:
            return False

        if not self.started:
            return False

        try:

            self._icon.notify(
                msg,
                title
            )

            return True

        except Exception as e:

            print(
                f"Не удалось показать уведомление трея: {e}"
            )

            return False

    def stop(
        self
    ):

        self.started = False

        if self._icon:

            try:

                self._icon.stop()

            except Exception:
                pass


# =====================================================
# COMMANDS WINDOW
# =====================================================

class CommandsWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        commands_path: str
    ):

        super().__init__(
            master
        )

        self.master_window = master
        self.commands_path = commands_path
        self.commands_data = {}
        self.filtered_commands = []
        self.active_category = "Все"
        self.selected_command_name = None

        self.title(
            "Команды AAYA"
        )

        self.geometry(
            "980x620"
        )

        self.minsize(
            850,
            520
        )

        # =================================================
        # Чтобы окно НЕ уходило под главное
        # =================================================

        try:
            self.transient(
                master
            )
        except Exception:
            pass

        try:
            self.lift()
            self.focus_force()
            self.attributes(
                "-topmost",
                True
            )

            self.after(
                300,
                lambda:
                self.attributes(
                    "-topmost",
                    False
                )
            )

        except Exception:
            pass

        try:
            self.protocol(
                "WM_DELETE_WINDOW",
                self.destroy
            )
        except Exception:
            pass

        self.grid_columnconfigure(
            0,
            weight=0
        )

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            2,
            weight=1
        )

        # =================================================
        # HEADER
        # =================================================

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=18,
            pady=(16, 8),
            sticky="ew"
        )

        header.grid_columnconfigure(
            0,
            weight=1
        )

        title = ctk.CTkLabel(
            header,
            text="Команды AAYA",
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            )
        )

        title.grid(
            row=0,
            column=0,
            sticky="w"
        )

        close_btn = ctk.CTkButton(
            header,
            text="Закрыть",
            width=110,
            height=34,
            corner_radius=12,
            command=self.destroy
        )

        close_btn.grid(
            row=0,
            column=1,
            sticky="e"
        )

        subtitle = ctk.CTkLabel(
            self,
            text="Выбери категорию или найди команду по названию, примеру или фразе.",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        )

        subtitle.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=18,
            pady=(0, 10),
            sticky="w"
        )

        # =================================================
        # LEFT PANEL: CATEGORIES
        # =================================================

        self.left_panel = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=16
        )

        self.left_panel.grid(
            row=2,
            column=0,
            padx=(18, 10),
            pady=(0, 18),
            sticky="ns"
        )

        self.left_panel.grid_propagate(
            False
        )

        ctk.CTkLabel(
            self.left_panel,
            text="Категории",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=14,
            pady=(14, 8)
        )

        self.category_frame = ctk.CTkScrollableFrame(
            self.left_panel,
            fg_color="transparent"
        )

        self.category_frame.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 10)
        )

        # =================================================
        # RIGHT PANEL
        # =================================================

        self.right_panel = ctk.CTkFrame(
            self,
            corner_radius=16
        )

        self.right_panel.grid(
            row=2,
            column=1,
            padx=(0, 18),
            pady=(0, 18),
            sticky="nsew"
        )

        self.right_panel.grid_columnconfigure(
            0,
            weight=1
        )

        self.right_panel.grid_rowconfigure(
            2,
            weight=1
        )

        # =================================================
        # SEARCH
        # =================================================

        search_row = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )

        search_row.grid(
            row=0,
            column=0,
            padx=14,
            pady=(14, 8),
            sticky="ew"
        )

        search_row.grid_columnconfigure(
            0,
            weight=1
        )

        self.search_entry = ctk.CTkEntry(
            search_row,
            height=38,
            corner_radius=12,
            placeholder_text="Поиск: ютуб, задача, время, пароль, перевод..."
        )

        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10)
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self._on_search_change
        )

        clear_btn = ctk.CTkButton(
            search_row,
            text="Очистить",
            width=100,
            height=38,
            corner_radius=12,
            command=self._clear_search
        )

        clear_btn.grid(
            row=0,
            column=1
        )

        self.info_label = ctk.CTkLabel(
            self.right_panel,
            text="",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        )

        self.info_label.grid(
            row=1,
            column=0,
            padx=14,
            pady=(0, 8),
            sticky="w"
        )

        # =================================================
        # CONTENT SPLIT
        # =================================================

        content = ctk.CTkFrame(
            self.right_panel,
            fg_color="transparent"
        )

        content.grid(
            row=2,
            column=0,
            padx=14,
            pady=(0, 14),
            sticky="nsew"
        )

        content.grid_columnconfigure(
            0,
            weight=1
        )

        content.grid_columnconfigure(
            1,
            weight=1
        )

        content.grid_rowconfigure(
            0,
            weight=1
        )

        # =================================================
        # COMMAND LIST
        # =================================================

        self.commands_list_frame = ctk.CTkScrollableFrame(
            content,
            corner_radius=14
        )

        self.commands_list_frame.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="nsew"
        )

        # =================================================
        # DETAILS PANEL
        # =================================================

        self.details_frame = ctk.CTkFrame(
            content,
            corner_radius=14
        )

        self.details_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.details_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.details_title = ctk.CTkLabel(
            self.details_frame,
            text="Выбери команду",
            font=ctk.CTkFont(
                size=21,
                weight="bold"
            ),
            anchor="w"
        )

        self.details_title.grid(
            row=0,
            column=0,
            padx=16,
            pady=(16, 4),
            sticky="ew"
        )

        self.details_category = ctk.CTkLabel(
            self.details_frame,
            text="",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#8E8E8E",
            anchor="w"
        )

        self.details_category.grid(
            row=1,
            column=0,
            padx=16,
            pady=(0, 12),
            sticky="ew"
        )

        self.details_textbox = ctk.CTkTextbox(
            self.details_frame,
            wrap="word",
            corner_radius=12
        )

        self.details_textbox.grid(
            row=2,
            column=0,
            padx=16,
            pady=(0, 16),
            sticky="nsew"
        )

        self.details_frame.grid_rowconfigure(
            2,
            weight=1
        )

        self.details_textbox.configure(
            state="disabled"
        )

        # =================================================
        # LOAD
        # =================================================

        self._load_commands()
        self._render_categories()
        self._apply_filter()

    # =====================================================
    # LOAD DATA
    # =====================================================

    def _load_commands(
        self
    ):

        try:

            with open(
                self.commands_path,
                "r",
                encoding="utf-8"
            ) as f:

                self.commands_data = json.load(
                    f
                )

        except Exception as e:

            self.commands_data = {}

            messagebox.showerror(
                "AAYA",
                f"Не удалось загрузить commands.json:\n{e}"
            )

    # =====================================================
    # CATEGORIES
    # =====================================================

    def _get_categories(
        self
    ):

        categories = {
            "Все"
        }

        for info in self.commands_data.values():

            categories.add(
                info.get(
                    "category",
                    "Другое"
                )
            )

        preferred = [
            "Все",
            "Общение",
            "Система",
            "Приложения",
            "Сайты",
            "Поиск",
            "Инструменты",
            "TODO",
            "Развлечения",
            "Другое"
        ]

        result = []

        for category in preferred:

            if category in categories:

                result.append(
                    category
                )

        for category in sorted(
            categories
        ):

            if category not in result:

                result.append(
                    category
                )

        return result

    def _count_category(
        self,
        category: str
    ) -> int:

        if category == "Все":

            return len(
                self.commands_data
            )

        count = 0

        for info in self.commands_data.values():

            if info.get(
                "category",
                "Другое"
            ) == category:

                count += 1

        return count

    def _render_categories(
        self
    ):

        for widget in self.category_frame.winfo_children():

            widget.destroy()

        for category in self._get_categories():

            count = self._count_category(
                category
            )

            text = (
                f"Все команды  ·  {count}"
                if category == "Все"
                else f"{category}  ·  {count}"
            )

            btn = ctk.CTkButton(
                self.category_frame,
                text=text,
                height=38,
                anchor="w",
                corner_radius=12,
                fg_color=(
                    "#1F6AA5"
                    if category == self.active_category
                    else "transparent"
                ),
                hover_color="#2B2B2B",
                command=lambda c=category:
                self._select_category(
                    c
                )
            )

            btn.pack(
                fill="x",
                pady=4
            )

    def _select_category(
        self,
        category: str
    ):

        self.active_category = category

        self._render_categories()
        self._apply_filter()

    # =====================================================
    # FILTER
    # =====================================================

    def _on_search_change(
        self,
        event=None
    ):

        self._apply_filter()

    def _clear_search(
        self
    ):

        self.search_entry.delete(
            0,
            "end"
        )

        self._apply_filter()

    def _matches_search(
        self,
        command_name: str,
        info: dict,
        query: str
    ) -> bool:

        if not query:
            return True

        parts = [
            command_name,
            info.get(
                "title",
                ""
            ),
            info.get(
                "description",
                ""
            ),
            info.get(
                "category",
                ""
            ),
            " ".join(
                info.get(
                    "examples",
                    []
                )
            ),
            " ".join(
                info.get(
                    "phrases",
                    []
                )
            )
        ]

        haystack = " ".join(
            parts
        ).lower()

        return query.lower() in haystack

    def _apply_filter(
        self
    ):

        query = (
            self.search_entry.get()
            or ""
        ).strip()

        visible = []

        for command_name, info in self.commands_data.items():

            category = info.get(
                "category",
                "Другое"
            )

            if (
                self.active_category != "Все"
                and category != self.active_category
            ):

                continue

            if not self._matches_search(
                command_name,
                info,
                query
            ):

                continue

            visible.append(
                (
                    command_name,
                    info
                )
            )

        self.filtered_commands = visible

        self.info_label.configure(
            text=f"Найдено команд: {len(visible)}"
        )

        self._render_command_list()

        if visible:

            first_name, first_info = visible[0]

            self._show_details(
                first_name,
                first_info
            )

        else:

            self._clear_details()

    # =====================================================
    # COMMAND LIST
    # =====================================================

    def _render_command_list(
        self
    ):

        for widget in self.commands_list_frame.winfo_children():

            widget.destroy()

        if not self.filtered_commands:

            empty = ctk.CTkLabel(
                self.commands_list_frame,
                text="Ничего не найдено",
                font=ctk.CTkFont(
                    size=14
                ),
                text_color="#A8A8A8"
            )

            empty.pack(
                pady=30
            )

            return

        for command_name, info in self.filtered_commands:

            title = info.get(
                "title",
                command_name
            )

            category = info.get(
                "category",
                "Другое"
            )

            examples = info.get(
                "examples",
                []
            )

            example_text = (
                examples[0]
                if examples
                else command_name
            )

            card = ctk.CTkButton(
                self.commands_list_frame,
                text=f"{title}\n{category} · {example_text}",
                anchor="w",
                height=66,
                corner_radius=12,
                fg_color=(
                    "#1F6AA5"
                    if command_name == self.selected_command_name
                    else "#2B2B2B"
                ),
                hover_color="#33383F",
                command=lambda n=command_name, i=info:
                self._show_details(
                    n,
                    i
                )
            )

            card.pack(
                fill="x",
                padx=4,
                pady=5
            )

    # =====================================================
    # DETAILS
    # =====================================================

    def _clear_details(
        self
    ):

        self.selected_command_name = None

        self.details_title.configure(
            text="Ничего не найдено"
        )

        self.details_category.configure(
            text=""
        )

        self.details_textbox.configure(
            state="normal"
        )

        self.details_textbox.delete(
            "1.0",
            "end"
        )

        self.details_textbox.insert(
            "1.0",
            "Попробуй изменить запрос или выбрать другую категорию."
        )

        self.details_textbox.configure(
            state="disabled"
        )

    def _show_details(
        self,
        command_name: str,
        info: dict
    ):

        self.selected_command_name = command_name

        title = info.get(
            "title",
            command_name
        )

        category = info.get(
            "category",
            "Другое"
        )

        description = info.get(
            "description",
            ""
        )

        action = info.get(
            "action",
            ""
        )

        examples = info.get(
            "examples",
            []
        )

        phrases = info.get(
            "phrases",
            []
        )

        self.details_title.configure(
            text=title
        )

        self.details_category.configure(
            text=f"{category} · {command_name}"
        )

        lines = []

        if description:

            lines.append(
                "Описание:"
            )

            lines.append(
                description
            )

            lines.append(
                ""
            )

        if examples:

            lines.append(
                "Примеры:"
            )

            for example in examples:

                lines.append(
                    f"• {example}"
                )

            lines.append(
                ""
            )

        if phrases:

            lines.append(
                "Можно сказать:"
            )

            for phrase in phrases:

                lines.append(
                    f"• {phrase}"
                )

            lines.append(
                ""
            )

        if action:

            lines.append(
                "Действие:"
            )

            lines.append(
                action
            )

        text = "\n".join(
            lines
        ).strip()

        if not text:

            text = "Для этой команды нет описания."

        self.details_textbox.configure(
            state="normal"
        )

        self.details_textbox.delete(
            "1.0",
            "end"
        )

        self.details_textbox.insert(
            "1.0",
            text
        )

        self.details_textbox.configure(
            state="disabled"
        )

        self._render_command_list()

# =====================================================
# MAIN GUI
# =====================================================

class AssistantGUI:

    def __init__(
        self,
        root,
        app_window=None
    ):

        self.root = root
        self.app_window = app_window or root.winfo_toplevel()

        self.ctx = detect_platform()

        self.notifier = Notifier(
            self.ctx,
            app_id="AAYA",
            root=self.app_window
        )

        self.hotkeys = Hotkeys()

        self.speaker = Speaker(
            enabled=True
        )

        self.commands_path = resource_path(
            "commands.json"
        )

        self.commands = self._load_commands(
            self.commands_path
        )

        self.processor = CommandProcessor(
            self.commands
        )

        self.exit_phrases = self._extract_exit_phrases(
            self.commands
        )

        self.recognizer = sr.Recognizer()

        self._listen_lock = threading.Lock()
        self._listening = False

        self._last_text_handled = ""
        self._last_text_time = 0.0

        self._closing = False

        self._system_lines = []

        self._build_ui()

        self.tray = Tray(
            "AAYA",
            open_cb=self._tray_open_safe,
            exit_cb=self._tray_exit_safe
        )

        self.tray_available = self.tray.start()
        self.notifier.tray = self.tray

        if self.tray_available:

            self._add_system_status(
                "Трей запущен"
            )

        else:

            self._add_system_status(
                "Трей недоступен"
            )

        if self.hotkeys.available:

            ok = self.hotkeys.register(
                HOTKEY,
                self.start_listening
            )

            if ok:

                self._add_system_status(
                    f"Hotkey: {HOTKEY}"
                )

            else:

                self._add_system_status(
                    f"Hotkey не зарегистрирован: {HOTKEY}"
                )

        else:

            self._add_system_status(
                "Hotkey недоступен"
            )

        self._add_system_status(
            f"ОС: {self.ctx.os_name.capitalize()}"
        )

        self._add_assistant_message(
            "Привет! Я AAYA.\n\n"
            "Я могу открывать приложения и сайты, создавать задачи и заметки, "
            "считать, переводить, запускать таймер и выполнять голосовые команды."
        )

        if hasattr(
            self.app_window,
            "protocol"
        ):

            self.app_window.protocol(
                "WM_DELETE_WINDOW",
                self.hide_to_tray
            )

    # =====================================================
    # TRAY SAFE CALLBACKS
    # =====================================================

    def _tray_open_safe(
        self
    ):

        try:

            self.root.after(
                0,
                self.show_window
            )

        except Exception:
            pass

    def _tray_exit_safe(
        self
    ):

        try:

            self.root.after(
                0,
                self.exit_app
            )

        except Exception:
            pass

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(
        self
    ):

        self.root.grid_columnconfigure(
            0,
            weight=1
        )

        self.root.grid_rowconfigure(
            0,
            weight=1
        )

        self.main = ctk.CTkFrame(
            self.root,
            corner_radius=22
        )

        self.main.grid(
            row=0,
            column=0,
            padx=16,
            pady=16,
            sticky="nsew"
        )

        self.main.grid_columnconfigure(
            0,
            weight=1
        )

        self.main.grid_rowconfigure(
            2,
            weight=1
        )

        # =================================================
        # HEADER
        # =================================================

        self.header = ctk.CTkFrame(
            self.main,
            corner_radius=18,
            height=92
        )

        self.header.grid(
            row=0,
            column=0,
            padx=14,
            pady=(14, 10),
            sticky="ew"
        )

        self.header.grid_columnconfigure(
            0,
            weight=1
        )

        self.header.grid_columnconfigure(
            1,
            weight=0
        )

        left_header = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        left_header.grid(
            row=0,
            column=0,
            padx=18,
            pady=14,
            sticky="w"
        )

        self.title_label = ctk.CTkLabel(
            left_header,
            text="AAYA Assistant",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        )

        self.title_label.pack(
            anchor="w"
        )

        self.subtitle_label = ctk.CTkLabel(
            left_header,
            text="Голосовой помощник для команд, задач и заметок",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#A8A8A8"
        )

        self.subtitle_label.pack(
            anchor="w",
            pady=(2, 0)
        )

        right_header = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        right_header.grid(
            row=0,
            column=1,
            padx=18,
            pady=14,
            sticky="e"
        )

        self.status_badge = ctk.CTkLabel(
            right_header,
            text="● Готов",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#7CFF95"
        )

        self.status_badge.pack(
            anchor="e"
        )

        self.mic_badge = ctk.CTkLabel(
            right_header,
            text="Микрофон: выкл",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#B7B7B7"
        )

        self.mic_badge.pack(
            anchor="e",
            pady=(6, 0)
        )

        self.system_status_label = ctk.CTkLabel(
            right_header,
            text="",
            font=ctk.CTkFont(
                size=11
            ),
            text_color="#858585"
        )

        self.system_status_label.pack(
            anchor="e",
            pady=(6, 0)
        )

        # =================================================
        # QUICK ACTIONS
        # =================================================

        self.quick_actions = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )

        self.quick_actions.grid(
            row=1,
            column=0,
            padx=14,
            pady=(0, 10),
            sticky="ew"
        )

        for i in range(
            5
        ):

            self.quick_actions.grid_columnconfigure(
                i,
                weight=1
            )

        self.quick_voice_btn = ctk.CTkButton(
            self.quick_actions,
            text="🎤 Слушать",
            height=38,
            corner_radius=14,
            command=self.start_listening
        )

        self.quick_voice_btn.grid(
            row=0,
            column=0,
            padx=(0, 8),
            sticky="ew"
        )

        self.quick_task_btn = ctk.CTkButton(
            self.quick_actions,
            text="✅ Новая задача",
            height=38,
            corner_radius=14,
            command=self._prefill_task
        )

        self.quick_task_btn.grid(
            row=0,
            column=1,
            padx=(0, 8),
            sticky="ew"
        )

        self.quick_note_btn = ctk.CTkButton(
            self.quick_actions,
            text="📝 Новая заметка",
            height=38,
            corner_radius=14,
            command=self._prefill_note
        )

        self.quick_note_btn.grid(
            row=0,
            column=2,
            padx=(0, 8),
            sticky="ew"
        )

        self.quick_cmds_btn = ctk.CTkButton(
            self.quick_actions,
            text="📚 Команды",
            height=38,
            corner_radius=14,
            command=self.open_commands_window
        )

        self.quick_cmds_btn.grid(
            row=0,
            column=3,
            padx=(0, 8),
            sticky="ew"
        )

        self.clear_chat_btn = ctk.CTkButton(
            self.quick_actions,
            text="🧹 Очистить чат",
            height=38,
            corner_radius=14,
            fg_color="#3B3B3B",
            hover_color="#4B4B4B",
            command=self.clear_chat
        )

        self.clear_chat_btn.grid(
            row=0,
            column=4,
            sticky="ew"
        )

        # =================================================
        # CHAT AREA
        # =================================================

        self.chat_card = ctk.CTkFrame(
            self.main,
            corner_radius=20
        )

        self.chat_card.grid(
            row=2,
            column=0,
            padx=14,
            pady=(0, 10),
            sticky="nsew"
        )

        self.chat_card.grid_columnconfigure(
            0,
            weight=1
        )

        self.chat_card.grid_rowconfigure(
            0,
            weight=1
        )

        self.chat_frame = ctk.CTkScrollableFrame(
            self.chat_card,
            corner_radius=18
        )

        self.chat_frame.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        self.chat_frame.grid_columnconfigure(
            0,
            weight=1
        )

        # =================================================
        # COMPOSER
        # =================================================

        self.bottom_card = ctk.CTkFrame(
            self.main,
            corner_radius=18
        )

        self.bottom_card.grid(
            row=3,
            column=0,
            padx=14,
            pady=(0, 14),
            sticky="ew"
        )

        self.bottom_card.grid_columnconfigure(
            0,
            weight=1
        )

        self.entry = ctk.CTkEntry(
            self.bottom_card,
            height=44,
            corner_radius=14,
            placeholder_text="Напиши команду... Например: создай задачу завтра купить продукты"
        )

        self.entry.grid(
            row=0,
            column=0,
            padx=12,
            pady=(12, 10),
            sticky="ew"
        )

        self.entry.bind(
            "<Return>",
            self._on_enter
        )

        actions_row = ctk.CTkFrame(
            self.bottom_card,
            fg_color="transparent"
        )

        actions_row.grid(
            row=1,
            column=0,
            padx=12,
            pady=(0, 8),
            sticky="ew"
        )

        for i in range(
            3
        ):

            actions_row.grid_columnconfigure(
                i,
                weight=1
            )

        self.btn_voice = ctk.CTkButton(
            actions_row,
            text="🎤 Голосовая команда",
            height=40,
            corner_radius=14,
            command=self.start_listening
        )

        self.btn_voice.grid(
            row=0,
            column=0,
            padx=(0, 8),
            sticky="ew"
        )

        self.btn_text = ctk.CTkButton(
            actions_row,
            text="➜ Отправить",
            height=40,
            corner_radius=14,
            command=self.run_text_command
        )

        self.btn_text.grid(
            row=0,
            column=1,
            padx=(0, 8),
            sticky="ew"
        )

        self.btn_cmds = ctk.CTkButton(
            actions_row,
            text="📄 Список команд",
            height=40,
            corner_radius=14,
            command=self.open_commands_window
        )

        self.btn_cmds.grid(
            row=0,
            column=2,
            sticky="ew"
        )

        footer = ctk.CTkFrame(
            self.bottom_card,
            fg_color="transparent"
        )

        footer.grid(
            row=2,
            column=0,
            padx=12,
            pady=(0, 10),
            sticky="ew"
        )

        footer.grid_columnconfigure(
            0,
            weight=1
        )

        self.status = ctk.CTkLabel(
            footer,
            text="Статус: ожидание",
            font=ctk.CTkFont(
                size=13
            ),
            text_color="#B0B0B0"
        )

        self.status.grid(
            row=0,
            column=0,
            sticky="w"
        )

        footer_right = ctk.CTkFrame(
            footer,
            fg_color="transparent"
        )

        footer_right.grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.hotkey_hint = ctk.CTkLabel(
            footer_right,
            text="Hotkey: Ctrl+Shift+Space",
            font=ctk.CTkFont(
                size=12
            ),
            text_color="#8E8E8E"
        )

        self.hotkey_hint.pack(
            side="left",
            padx=(0, 14)
        )

        self.theme_switch = ctk.CTkSwitch(
            footer_right,
            text="Light / Dark",
            command=self.toggle_theme
        )

        self.theme_switch.pack(
            side="left"
        )

        try:

            current = ctk.get_appearance_mode()

            if current.lower() == "dark":

                self.theme_switch.select()

            else:

                self.theme_switch.deselect()

        except Exception:

            self.theme_switch.select()

    # =====================================================
    # CHAT MESSAGES
    # =====================================================

    def _scroll_chat_to_bottom(
        self
    ):

        try:

            self.chat_frame._parent_canvas.yview_moveto(
                1.0
            )

        except Exception:
            pass

    def _add_message(
        self,
        text: str,
        kind: str = "assistant"
    ):

        text = (
            text or ""
        ).strip()

        if not text:
            return

        row = ctk.CTkFrame(
            self.chat_frame,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            pady=7,
            padx=6
        )

        if kind == "user":

            bubble_color = "#1F6AA5"
            text_color = "#FFFFFF"
            title_color = "#D4E9FF"
            label_title = "Ты"
            side = "right"
            anchor = "e"
            wrap = 560

        elif kind == "system":

            bubble_color = "#2A2A2A"
            text_color = "#BEBEBE"
            title_color = "#9A9A9A"
            label_title = "Система"
            side = "top"
            anchor = "center"
            wrap = 650

        else:

            bubble_color = "#22252A"
            text_color = "#F0F0F0"
            title_color = "#A0CFFF"
            label_title = "AAYA"
            side = "left"
            anchor = "w"
            wrap = 560

        bubble = ctk.CTkFrame(
            row,
            corner_radius=18,
            fg_color=bubble_color
        )

        if kind == "system":

            bubble.pack(
                anchor=anchor,
                pady=2
            )

        else:

            bubble.pack(
                side=side,
                anchor=anchor,
                padx=6
            )

        title = ctk.CTkLabel(
            bubble,
            text=label_title,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color=title_color,
            anchor="w"
        )

        title.pack(
            anchor="w",
            padx=14,
            pady=(10, 2)
        )

        msg = ctk.CTkLabel(
            bubble,
            text=text,
            justify="left",
            wraplength=wrap,
            anchor="w",
            text_color=text_color,
            font=ctk.CTkFont(
                size=14
            )
        )

        msg.pack(
            anchor="w",
            padx=14,
            pady=(0, 12)
        )

        self.root.after(
            80,
            self._scroll_chat_to_bottom
        )

    def _add_user_message(
        self,
        text: str
    ):

        self._add_message(
            text,
            "user"
        )

    def _add_assistant_message(
        self,
        text: str
    ):

        self._add_message(
            text,
            "assistant"
        )

    def _add_system_message(
        self,
        text: str
    ):

        self._add_message(
            text,
            "system"
        )

    def clear_chat(
        self
    ):

        for widget in self.chat_frame.winfo_children():

            widget.destroy()

        self._add_assistant_message(
            "Чат очищен. Чем займёмся?"
        )

    def _add_system_status(
        self,
        text: str
    ):

        text = (
            text or ""
        ).strip()

        if not text:
            return

        self._system_lines.append(
            text
        )

        self._system_lines = self._system_lines[
            -3:
        ]

        try:

            self.system_status_label.configure(
                text=" · ".join(
                    self._system_lines
                )
            )

        except Exception:
            pass

        print(
            text
        )

    # =====================================================
    # STATUS
    # =====================================================

    def set_status(
        self,
        text: str
    ):

        self.status.configure(
            text=text
        )

        low = text.lower()

        if "слушаю" in low:

            self.status_badge.configure(
                text="● Слушаю",
                text_color="#FFD66B"
            )

        elif "выполняю" in low:

            self.status_badge.configure(
                text="● Работаю",
                text_color="#7FDBFF"
            )

        else:

            self.status_badge.configure(
                text="● Готов",
                text_color="#7CFF95"
            )

    def set_mic(
        self,
        on: bool
    ):

        if on:

            self.mic_badge.configure(
                text="Микрофон: ВКЛ",
                text_color="#7CFF95"
            )

        else:

            self.mic_badge.configure(
                text="Микрофон: выкл",
                text_color="#B7B7B7"
            )

    # =====================================================
    # QUICK ACTIONS
    # =====================================================

    def _prefill_task(
        self
    ):

        self.entry.delete(
            0,
            "end"
        )

        self.entry.insert(
            0,
            "создай задачу "
        )

        self.entry.focus()

    def _prefill_note(
        self
    ):

        self.entry.delete(
            0,
            "end"
        )

        self.entry.insert(
            0,
            "создай заметку "
        )

        self.entry.focus()

    # =====================================================
    # THEME
    # =====================================================

    def toggle_theme(
        self
    ):

        try:

            if self.theme_switch.get() == 1:

                ctk.set_appearance_mode(
                    "dark"
                )

            else:

                ctk.set_appearance_mode(
                    "light"
                )

        except Exception:
            pass

    # =====================================================
    # EVENTS
    # =====================================================

    def _on_enter(
        self,
        event=None
    ):

        self.run_text_command()

        return "break"

    def open_commands_window(
        self
    ):

        # Если окно команд уже открыто — просто поднимаем его наверх,
        # а не создаём новое. Это убирает лаги и дубли окон.
        if hasattr(
            self,
            "_commands_window"
        ):

            try:

                if self._commands_window.winfo_exists():

                    self._commands_window.lift()
                    self._commands_window.focus_force()

                    try:
                        self._commands_window.attributes(
                            "-topmost",
                            True
                        )

                        self._commands_window.after(
                            250,
                            lambda:
                            self._commands_window.attributes(
                                "-topmost",
                                False
                            )
                        )

                    except Exception:
                        pass

                    return

            except Exception:
                pass

        self._commands_window = CommandsWindow(
            self.app_window,
            self.commands_path
        )

        self._commands_window.focus_force()

    # =====================================================
    # LOAD COMMANDS
    # =====================================================

    def _load_commands(
        self,
        path: str
    ) -> dict:

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(
                    f
                )

        except Exception as e:

            messagebox.showerror(
                "AAYA",
                f"Не удалось загрузить commands.json:\n{e}"
            )

            return {}

    def _extract_exit_phrases(
        self,
        commands: dict
    ) -> Set[str]:

        default = {
            "пока",
            "до свидания",
            "выключись",
            "закройся",
            "bye"
        }

        try:

            bye = commands.get(
                "bye",
                {}
            )

            phrases = bye.get(
                "phrases",
                []
            )

            s = {
                str(p).strip().lower()
                for p in phrases
                if str(p).strip()
            }

            return s or default

        except Exception:

            return default

    # =====================================================
    # TEXT COMMANDS
    # =====================================================

    def run_text_command(
        self
    ):

        text = (
            self.entry.get()
            or ""
        ).strip()

        if not text:
            return

        self.entry.delete(
            0,
            "end"
        )

        self._handle_text(
            text
        )

    def _handle_text(
        self,
        text: str
    ):

        norm = text.strip().lower()
        now = time.time()

        if (
            norm
            and norm == self._last_text_handled
            and (now - self._last_text_time) < 1.2
        ):

            return

        self._last_text_handled = norm
        self._last_text_time = now

        self._add_user_message(
            text
        )

        if norm in self.exit_phrases:

            self._add_assistant_message(
                "Выключаюсь."
            )

            self.notifier.toast(
                "AAYA",
                "Выключаюсь."
            )

            try:

                self.speaker.speak(
                    "Выключаюсь."
                )

            except Exception:
                pass

            self.exit_app()

            return

        self.set_status(
            "Статус: выполняю команду"
        )

        buf = io.StringIO()

        try:

            with redirect_stdout(
                buf
            ):

                self.processor.handle(
                    norm
                )

        except Exception as e:

            print(
                f"Ошибка выполнения команды: {e}",
                file=buf
            )

        raw = buf.getvalue()

        cleaned = _clean_output_lines(
            raw
        )

        answer = _final_answer_from_captured(
            raw
        ) or "Готово."

        if len(
            cleaned
        ) > 1:

            shown_lines = []

            for line in cleaned:

                if line not in shown_lines:

                    shown_lines.append(
                        line
                    )

            visual_answer = "\n".join(
                shown_lines
            )

        else:

            visual_answer = answer

        self._add_assistant_message(
            visual_answer
        )

        self.notifier.toast(
            "AAYA",
            answer
        )

        try:

            self.speaker.speak(
                answer
            )

        except Exception as e:

            print(
                f"Ошибка запуска озвучки: {e}"
            )

        self.set_status(
            "Статус: ожидание"
        )

    # =====================================================
    # VOICE COMMANDS
    # =====================================================

    def start_listening(
        self
    ):

        if self._listening:
            return

        if not self._listen_lock.acquire(
            blocking=False
        ):

            return

        self._listening = True

        self.root.after(
            0,
            lambda:
            self.set_mic(
                True
            )
        )

        self.root.after(
            0,
            lambda:
            self.set_status(
                "Статус: слушаю"
            )
        )

        self.root.after(
            0,
            lambda:
            self._add_system_status(
                "Слушаю..."
            )
        )

        self.notifier.toast(
            "AAYA",
            "🎤 Слушаю…"
        )

        t = threading.Thread(
            target=self._listen_thread,
            daemon=True
        )

        t.start()

    def _listen_thread(
        self
    ):

        try:

            with sr.Microphone() as source:

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=8
                )

            try:

                text = self.recognizer.recognize_google(
                    audio,
                    language="ru-RU"
                )

                text = (
                    text
                    or ""
                ).strip()

            except sr.UnknownValueError:

                text = ""

            except sr.RequestError as e:

                text = ""

                self.notifier.toast(
                    "AAYA",
                    "Ошибка сервиса распознавания речи."
                )

                self.root.after(
                    0,
                    lambda err=e:
                    self._add_system_status(
                        f"Ошибка сервиса распознавания: {err}"
                    )
                )

            except Exception as e:

                text = ""

                self.root.after(
                    0,
                    lambda err=e:
                    self._add_system_status(
                        f"Ошибка распознавания: {err}"
                    )
                )

            if text:

                self.root.after(
                    0,
                    lambda t=text:
                    self._handle_text(
                        t
                    )
                )

            else:

                self.root.after(
                    0,
                    lambda:
                    self._add_system_status(
                        "Ничего не распознано"
                    )
                )

        except Exception as e:

            self.notifier.toast(
                "AAYA",
                "Ошибка микрофона или доступа к аудио."
            )

            self.root.after(
                0,
                lambda err=e:
                self._add_system_status(
                    f"Ошибка микрофона: {repr(err)}"
                )
            )

        finally:

            self._listening = False

            try:

                self._listen_lock.release()

            except Exception:
                pass

            self.root.after(
                0,
                lambda:
                self.set_mic(
                    False
                )
            )

            self.root.after(
                0,
                lambda:
                self.set_status(
                    "Статус: ожидание"
                )
            )

    # =====================================================
    # TRAY BEHAVIOR
    # =====================================================

    def hide_to_tray(
        self
    ):

        if getattr(
            self,
            "tray_available",
            False
        ):

            try:

                self.app_window.withdraw()

                self.notifier.toast(
                    "AAYA",
                    "Работаю в фоне. Открыть можно из трея."
                )

                return

            except Exception as e:

                print(
                    f"Ошибка скрытия в трей: {e}"
                )

        try:

            self.app_window.iconify()

            self.notifier.toast(
                "AAYA",
                "Трей недоступен, окно просто свернуто."
            )

        except Exception as e:

            print(
                f"Ошибка сворачивания окна: {e}"
            )

    def show_window(
        self
    ):

        try:

            self.app_window.deiconify()
            self.app_window.lift()
            self.app_window.focus_force()

            try:

                self.app_window.attributes(
                    "-topmost",
                    True
                )

                self.app_window.after(
                    150,
                    lambda:
                    self.app_window.attributes(
                        "-topmost",
                        False
                    )
                )

            except Exception:
                pass

        except Exception as e:

            print(
                f"Ошибка открытия окна: {e}"
            )

    def exit_app(
        self
    ):

        if self._closing:
            return

        self._closing = True

        try:

            self.speaker.stop()

        except Exception:
            pass

        try:

            self.hotkeys.unregister_all()

        except Exception:
            pass

        try:

            self.tray.stop()

        except Exception:
            pass

        try:

            self.app_window.destroy()

        except Exception:
            pass

        os._exit(
            0
        )