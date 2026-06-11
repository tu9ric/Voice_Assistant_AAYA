import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8765"

def _post(path: str, payload: dict | None = None, timeout: float = 1.5) -> dict:
    data = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def _get(path: str, timeout: float = 1.5) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def ping() -> bool:
    try:
        return bool(_get("/ping").get("ok"))
    except Exception:
        return False

def show():
    return _post("/ui/show")

def open_tab(name: str):
    return _post("/ui/open_tab", {"name": name})

def create_task(title: str, date: str, time_start=None, time_end=None, tag=None, description=""):
    return _post("/tasks/create", {
        "title": title,
        "date": date,
        "time_start": time_start,
        "time_end": time_end,
        "tag": tag,
        "description": description,
    })

def list_tasks(date: str | None = None, include_done: bool = True):
    q = "/tasks?done=" + ("1" if include_done else "0")
    if date:
        q += "&date=" + date
    return _get(q)

def done_task(task_id: int):
    return _post("/tasks/done", {"id": task_id})

def delete_task(task_id: int):
    return _post("/tasks/delete", {"id": task_id})