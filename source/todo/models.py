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
    remind_offsets_json: str = "[]"


@dataclass
class Note:
    id: int
    title: str
    body: str
    created_at: str


@dataclass
class User:
    id: int
    name: str
    email: str
    password_hash: str
    created_at: str