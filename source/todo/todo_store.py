import hashlib
import sqlite3
from typing import List, Optional
from datetime import datetime

from .paths import personal_db_path
from .models import Task, Note, User


class PersonalStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or personal_db_path()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time_start TEXT,
                time_end TEXT,
                tag TEXT,
                description TEXT DEFAULT '',
                done INTEGER DEFAULT 0,
                subtasks_json TEXT DEFAULT '[]',
                remind_offsets_json TEXT DEFAULT '[]',
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """)

            con.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """)

            con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            con.execute("""
            CREATE TABLE IF NOT EXISTS session (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """)

            con.execute("INSERT OR IGNORE INTO session(id, user_id) VALUES (1, NULL)")
            self._migrate(con)

    def _migrate(self, con: sqlite3.Connection) -> None:
        cur = con.cursor()

        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN subtasks_json TEXT DEFAULT '[]'")
        except Exception:
            pass

        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN remind_offsets_json TEXT DEFAULT '[]'")
        except Exception:
            pass

        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN user_id INTEGER")
        except Exception:
            pass

        try:
            cur.execute("ALTER TABLE notes ADD COLUMN user_id INTEGER")
        except Exception:
            pass

        con.commit()

    # -------- Helpers --------
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256((password or "").encode("utf-8")).hexdigest()

    def _require_user_id(self) -> int:
        user = self.get_current_user()
        if not user:
            raise ValueError("Сначала войдите в аккаунт.")
        return user.id

    # -------- Tasks --------
    def create_task(
        self,
        title: str,
        date: str,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        tag: Optional[str] = None,
        description: str = "",
        subtasks_json: str = "[]",
        remind_offsets_json: str = "[]",
    ) -> Task:
        user_id = self._require_user_id()

        title = (title or "").strip()
        if not title:
            raise ValueError("Пустое название задачи.")

        with self._conn() as con:
            cur = con.execute(
                """INSERT INTO tasks(
                       user_id, title, date, time_start, time_end, tag, description, done, subtasks_json, remind_offsets_json
                   )
                   VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
                (
                    user_id,
                    title,
                    date,
                    time_start,
                    time_end,
                    tag,
                    description or "",
                    subtasks_json or "[]",
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
            subtasks_json or "[]",
            remind_offsets_json or "[]",
        )

    def list_tasks(self, date: Optional[str] = None, include_done: bool = True) -> List[Task]:
        user = self.get_current_user()
        if not user:
            return []

        q = """
            SELECT id, title, date, time_start, time_end, tag, description, done, subtasks_json, remind_offsets_json
            FROM tasks
            WHERE user_id=?
        """
        params = [user.id]

        if date:
            q += " AND date=?"
            params.append(date)

        if not include_done:
            q += " AND done=0"

        q += " ORDER BY done ASC, date ASC, COALESCE(time_start,'') ASC, id ASC"

        with self._conn() as con:
            rows = con.execute(q, params).fetchall()

        return [Task(*r) for r in rows]

    def set_done(self, task_id: int, done: int = 1) -> None:
        self.update_task_done(task_id, done)

    def update_task_done(self, task_id: int, done: int) -> None:
        user_id = self._require_user_id()
        with self._conn() as con:
            cur = con.execute(
                "UPDATE tasks SET done=? WHERE id=? AND user_id=?",
                (1 if done else 0, task_id, user_id),
            )
            if cur.rowcount == 0:
                raise ValueError("Задача не найдена.")

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        date: Optional[str] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        tag: Optional[str] = None,
        description: Optional[str] = None,
        subtasks_json: Optional[str] = None,
        remind_offsets_json: Optional[str] = None,
    ) -> None:
        user_id = self._require_user_id()

        fields = []
        params = []

        if title is not None:
            fields.append("title=?")
            params.append(title)
        if date is not None:
            fields.append("date=?")
            params.append(date)
        if time_start is not None:
            fields.append("time_start=?")
            params.append(time_start)
        if time_end is not None:
            fields.append("time_end=?")
            params.append(time_end)
        if tag is not None:
            fields.append("tag=?")
            params.append(tag)
        if description is not None:
            fields.append("description=?")
            params.append(description)
        if subtasks_json is not None:
            fields.append("subtasks_json=?")
            params.append(subtasks_json)
        if remind_offsets_json is not None:
            fields.append("remind_offsets_json=?")
            params.append(remind_offsets_json)

        if not fields:
            return

        params.extend([task_id, user_id])

        with self._conn() as con:
            cur = con.execute(
                f"UPDATE tasks SET {', '.join(fields)} WHERE id=? AND user_id=?",
                params
            )
            if cur.rowcount == 0:
                raise ValueError("Задача не найдена.")

    def delete_task(self, task_id: int) -> None:
        user_id = self._require_user_id()
        with self._conn() as con:
            cur = con.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
            if cur.rowcount == 0:
                raise ValueError("Задача не найдена.")

    # -------- Notes --------
    def create_note(self, title: str, body: str) -> Note:
        user_id = self._require_user_id()

        title = (title or "").strip() or "Без названия"
        body = (body or "").strip()
        if not body:
            raise ValueError("Пустая заметка.")

        created = datetime.now().isoformat(timespec="seconds")

        with self._conn() as con:
            cur = con.execute(
                "INSERT INTO notes(user_id, title, body, created_at) VALUES (?, ?, ?, ?)",
                (user_id, title, body, created),
            )
            note_id = int(cur.lastrowid)

        return Note(note_id, title, body, created)

    def list_notes(self) -> List[Note]:
        user = self.get_current_user()
        if not user:
            return []

        with self._conn() as con:
            rows = con.execute(
                "SELECT id, title, body, created_at FROM notes WHERE user_id=? ORDER BY id DESC",
                (user.id,),
            ).fetchall()
        return [Note(*r) for r in rows]

    def update_note(self, note_id: int, title: str, body: str) -> None:
        user_id = self._require_user_id()

        title = (title or "").strip() or "Без названия"
        body = (body or "").strip()
        if not body:
            raise ValueError("Пустая заметка.")

        with self._conn() as con:
            cur = con.execute(
                "UPDATE notes SET title=?, body=? WHERE id=? AND user_id=?",
                (title, body, note_id, user_id),
            )
            if cur.rowcount == 0:
                raise ValueError("Заметка не найдена.")

    def delete_note(self, note_id: int) -> None:
        user_id = self._require_user_id()
        with self._conn() as con:
            cur = con.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, user_id))
            if cur.rowcount == 0:
                raise ValueError("Заметка не найдена.")

    # -------- Users / Session --------
    def register_user(self, name: str, email: str, password: str) -> User:
        name = (name or "").strip()
        email = (email or "").strip().lower()
        password = (password or "").strip()

        if not name:
            raise ValueError("Введите имя.")
        if not email:
            raise ValueError("Введите email.")
        if not password:
            raise ValueError("Введите пароль.")
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")

        created = datetime.now().isoformat(timespec="seconds")
        password_hash = self._hash_password(password)

        try:
            with self._conn() as con:
                cur = con.execute(
                    "INSERT INTO users(name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                    (name, email, password_hash, created),
                )
                user_id = int(cur.lastrowid)
                con.execute("UPDATE session SET user_id=? WHERE id=1", (user_id,))
        except sqlite3.IntegrityError:
            raise ValueError("Пользователь с таким email уже существует.")

        return User(user_id, name, email, password_hash, created)

    def login_user(self, email: str, password: str) -> User:
        email = (email or "").strip().lower()
        password_hash = self._hash_password(password or "")

        with self._conn() as con:
            row = con.execute(
                "SELECT id, name, email, password_hash, created_at FROM users WHERE email=?",
                (email,),
            ).fetchone()

            if not row:
                raise ValueError("Пользователь не найден.")

            user = User(*row)
            if user.password_hash != password_hash:
                raise ValueError("Неверный пароль.")

            con.execute("UPDATE session SET user_id=? WHERE id=1", (user.id,))

        return user

    def logout_user(self) -> None:
        with self._conn() as con:
            con.execute("UPDATE session SET user_id=NULL WHERE id=1")

    def get_current_user(self) -> Optional[User]:
        with self._conn() as con:
            row = con.execute("""
                SELECT u.id, u.name, u.email, u.password_hash, u.created_at
                FROM session s
                LEFT JOIN users u ON u.id = s.user_id
                WHERE s.id = 1
            """).fetchone()

        if not row or row[0] is None:
            return None
        return User(*row)