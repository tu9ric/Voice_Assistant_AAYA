from __future__ import annotations
from typing import Callable, Optional

from core.platform_context import PlatformContext


class Hotkeys:
    def __init__(self, ctx: PlatformContext):
        self.ctx = ctx
        self._keyboard = None
        self._enabled = False

        try:
            import keyboard  # type: ignore
            self._keyboard = keyboard
        except Exception:
            self._keyboard = None

    @property
    def available(self) -> bool:
        return self._keyboard is not None

    def register(self, hotkey: str, callback: Callable[[], None]) -> bool:
        """
        Возвращает True если зарегистрировалось.
        На Linux может требовать права/доступ (иногда root) и зависеть от X11/Wayland.
        """
        if not self._keyboard:
            return False
        try:
            self._keyboard.add_hotkey(hotkey, callback)
            self._enabled = True
            return True
        except Exception:
            return False

    def unregister_all(self) -> None:
        if not self._keyboard:
            return
        try:
            self._keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        self._enabled = False
