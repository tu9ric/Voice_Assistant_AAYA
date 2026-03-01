# source/todo/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    id: int
    title: str
    date: str
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    tag: Optional[str] = None
    description: str = ""
    done: int = 0

    subtasks_json: str = "[]"

    # было remind_at -> убираем (или оставь, но больше не используем)
    remind_offsets_json: str = "[]"   # например ["P2D","P1D","PT1H","PT15M"]

@dataclass
class Note:
    id: int
    title: str
    body: str
    created_at: str