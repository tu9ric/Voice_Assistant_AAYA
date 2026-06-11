import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from .todo_store import PersonalStore

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

class TodoAPI:
    def __init__(self, store: PersonalStore, ui_callbacks: dict,
                 host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """
        ui_callbacks: {
          "show": callable,
          "open_tab": callable(name:str)
        }
        """
        self.store = store
        self.ui = ui_callbacks
        self.host = host
        self.port = port
        self._srv = None
        self._thread = None

    def start(self):
        store = self.store
        ui = self.ui

        class Handler(BaseHTTPRequestHandler):
            def _json(self, code: int, payload: dict):
                data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _read_body(self) -> dict:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length > 0 else b"{}"
                try:
                    return json.loads(raw.decode("utf-8"))
                except Exception:
                    return {}

            def do_GET(self):
                p = urlparse(self.path)
                if p.path == "/ping":
                    return self._json(200, {"ok": True})

                if p.path == "/tasks":
                    qs = parse_qs(p.query)
                    date = (qs.get("date", [None])[0] or None)
                    include_done = (qs.get("done", ["1"])[0] == "1")
                    tasks = store.list_tasks(date=date, include_done=include_done)
                    return self._json(200, {"ok": True, "tasks": [t.__dict__ for t in tasks]})

                return self._json(404, {"ok": False, "error": "Not found"})

            def do_POST(self):
                p = urlparse(self.path)
                body = self._read_body()

                if p.path == "/ui/show":
                    try:
                        ui["show"]()
                    except Exception:
                        pass
                    return self._json(200, {"ok": True})

                if p.path == "/ui/open_tab":
                    name = (body.get("name") or "").strip()
                    try:
                        ui["open_tab"](name)
                    except Exception:
                        pass
                    return self._json(200, {"ok": True})

                if p.path == "/tasks/create":
                    try:
                        task = store.create_task(
                            title=body.get("title", ""),
                            date=body.get("date", ""),
                            time_start=body.get("time_start"),
                            time_end=body.get("time_end"),
                            tag=body.get("tag"),
                            description=body.get("description", "")
                        )
                        return self._json(200, {"ok": True, "task": task.__dict__})
                    except Exception as e:
                        return self._json(400, {"ok": False, "error": str(e)})

                if p.path == "/tasks/done":
                    try:
                        store.set_done(int(body.get("id")), 1)
                        return self._json(200, {"ok": True})
                    except Exception as e:
                        return self._json(400, {"ok": False, "error": str(e)})

                if p.path == "/tasks/delete":
                    try:
                        store.delete_task(int(body.get("id")))
                        return self._json(200, {"ok": True})
                    except Exception as e:
                        return self._json(400, {"ok": False, "error": str(e)})

                if p.path == "/notes/create":
                    try:
                        note = store.create_note(body.get("title", ""), body.get("body", ""))
                        return self._json(200, {"ok": True, "note": note.__dict__})
                    except Exception as e:
                        return self._json(400, {"ok": False, "error": str(e)})

                return self._json(404, {"ok": False, "error": "Not found"})

            def log_message(self, format, *args):
                # выключаем шум в консоль
                return

        self._srv = HTTPServer((self.host, self.port), Handler)

        def _run():
            try:
                self._srv.serve_forever()
            except Exception:
                pass

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            if self._srv:
                self._srv.shutdown()
        except Exception:
            pass