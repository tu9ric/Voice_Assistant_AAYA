import sqlite3
from typing import List, Optional
from datetime import datetime

from .paths import personal_db_path
from .models import Task, Note


class PersonalStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or personal_db_path()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        # Можно добавить check_same_thread=False, если будешь обращаться из потоков
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time_start TEXT,
                time_end TEXT,
                tag TEXT,
                description TEXT DEFAULT '',
                done INTEGER DEFAULT 0,
                subtasks_json TEXT DEFAULT '[]',
                remind_offsets_json TEXT DEFAULT '[]'
            );
            """)

            con.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            self._migrate(con)

    def _migrate(self, con: sqlite3.Connection) -> None:
        cur = con.cursor()

        # Старые БД могли не иметь этих колонок
        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN subtasks_json TEXT DEFAULT '[]'")
        except Exception:
            pass

        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN remind_offsets_json TEXT DEFAULT '[]'")
        except Exception:
            pass

        con.commit()

    # -------- Tasks --------
    def create_task(
        self,
        title: str,
        date: str,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        tag: Optional[str] = None,
        description: str = "",
        subt_json: str = "[]",
        remind_offsets_json: str = "[]",
    ) -> Task:
        title = (title or "").strip()
        if not title:
            raise ValueError("Пустое название задачи.")

        with self._conn() as con:
            cur = con.execute(
                """INSERT INTO tasks(title,date,time_start,time_end,tag,description,done,subtasks_json,remind_offsets_json)
                   VALUES (?,?,?,?,?,?,0,?,?)""",
                (
                    title,
                    date,
                    time_start,
                    time_end,
                    tag,
                    description or "",
                    subt_json or "[]",
                    remind_offsets_json or "[]",
                ),
            )
            task_id = int(cur.lastrowid)

        return Task(
            task_id,
            title,
            date,
            time_start,
            time_end,
            tag,
            description or "",
            0,
            subt_json or "[]",
            remind_offsets_json or "[]",
        )

    def list_tasks(self, date: Optional[str] = None, include_done: bool = True) -> List[Task]:
        q = """SELECT
                id,title,date,time_start,time_end,tag,description,done,subtasks_json,remind_offsets_json
               FROM tasks"""
        params = []
        where = []

        if date:
            where.append("date=?")
            params.append(date)

        if not include_done:
            where.append("done=0")

        if where:
            q += " WHERE " + " AND ".join(where)

        q += " ORDER BY date ASC, COALESCE(time_start,'') ASC, id ASC"

        with self._conn() as con:
            rows = con.execute(q, params).fetchall()

        return [Task(*r) for r in rows]

    # совместимость со старым кодом
    def set_done(self, task_id: int, done: int = 1) -> None:
        self.update_task_done(task_id, done)

    # для UI (чекбокс "выполнено")
    def update_task_done(self, task_id: int, done: int) -> None:
        with self._conn() as con:
            cur = con.execute("UPDATE tasks SET done=? WHERE id=?", (1 if done else 0, task_id))
            if cur.rowcount == 0:
                raise ValueError("Задача не найдена.")

    # на будущее (редактирование задач)
    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        date: Optional[str] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        tag: Optional[str] = None,
        description: Optional[str] = None,
        subt_json: Optional[str] = None,
        remind_offsets_json: Optional[str] = None,
    ) -> None:
        fields = []
        params = []

        if title is not None:
            fields.append("title=?"); params.append(title)
        if date is not None:
            fields.append("date=?"); params.append(date)
        if time_start is not None:
            fields.append("time_start=?"); params.append(time_start)
        if time_end is not None:
            fields.append("time_end=?"); params.append(time_end)
        if tag is not None:
            fields.append("tag=?"); params.append(tag)
        if description is not None:
            fields.append("description=?"); params.append(description)
        if subt_json is not None:
            fields.append("subtasks_json=?"); params.append(subt_json)
        if remind_offsets_json is not None:
            fields.append("remind_offsets_json=?"); params.append(remind_offsets_json)

        if not fields:
            return

        params.append(task_id)

        with self._conn() as con:
            cur = con.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id=?", params)
            if cur.rowcount == 0:
                raise ValueError("Задача не найдена.")

    def delete_task(self, task_id: int) -> None:
        with self._conn() as con:
            cur = con.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            if cur.rowcount == 0:
                raise ValueError("Задача не найдена.")

    # -------- Notes (локально) --------
    def create_note(self, title: str, body: str) -> Note:
        title = (title or "").strip() or "Без названия"
        body = (body or "").strip()
        if not body:
            raise ValueError("Пустая заметка.")

        created = datetime.now().isoformat(timespec="seconds")

        with self._conn() as con:
            cur = con.execute(
                "INSERT INTO notes(title,body,created_at) VALUES (?,?,?)",
                (title, body, created),
            )
            note_id = int(cur.lastrowid)

        return Note(note_id, title, body, created)

    def list_notes(self) -> List[Note]:
        with self._conn() as con:
            rows = con.execute(
                "SELECT id,title,body,created_at FROM notes ORDER BY id DESC"
            ).fetchall()
        return [Note(*r) for r in rows]