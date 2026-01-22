from __future__ import annotations
import os
import platform
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformContext:
    os_name: str          # "windows" / "linux" / "darwin"
    is_windows: bool
    is_linux: bool
    is_macos: bool
    is_frozen: bool       # PyInstaller onefile/onedir
    is_wayland: bool      # актуально для Linux
    is_x11: bool          # актуально для Linux


def detect_platform() -> PlatformContext:
    sys_name = platform.system().lower()  # windows/linux/darwin
    is_windows = sys_name == "windows"
    is_linux = sys_name == "linux"
    is_macos = sys_name == "darwin"

    is_frozen = bool(getattr(sys, "frozen", False))  # PyInstaller

    # Linux display server (может быть пусто)
    session_type = (os.environ.get("XDG_SESSION_TYPE") or "").lower()
    is_wayland = is_linux and session_type == "wayland"
    is_x11 = is_linux and (session_type == "x11" or session_type == "")

    return PlatformContext(
        os_name=sys_name,
        is_windows=is_windows,
        is_linux=is_linux,
        is_macos=is_macos,
        is_frozen=is_frozen,
        is_wayland=is_wayland,
        is_x11=is_x11,
    )
