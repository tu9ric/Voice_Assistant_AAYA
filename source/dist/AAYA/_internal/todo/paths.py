import os
from pathlib import Path

APP_NAME = "AAYA_TODO"

def app_data_dir() -> Path:
    # Windows: %APPDATA%/AAYA_TODO
    # Linux/macOS: ~/.AAYA_TODO
    base = os.getenv("APPDATA") or str(Path.home())
    p = Path(base) / APP_NAME
    p.mkdir(parents=True, exist_ok=True)
    return p

def personal_db_path() -> str:
    return str(app_data_dir() / "personal.db")

def group_cache_db_path() -> str:
    return str(app_data_dir() / "group_cache.db")

def attachments_dir() -> str:
    p = app_data_dir() / "attachments"
    p.mkdir(parents=True, exist_ok=True)
    return str(p)