import sqlite3
import threading
from pathlib import Path

class InMemoryReplayStore:
    def __init__(self):
        self._used: set[str] = set()
        self._lock = threading.Lock()
    def consume_once(self, authority_id: str) -> bool:
        with self._lock:
            if authority_id in self._used:
                return False
            self._used.add(authority_id)
            return True
    def is_used(self, authority_id: str) -> bool:
        with self._lock:
            return authority_id in self._used

class SQLiteReplayStore:
    """Durable local replay store with atomic UNIQUE insertion."""
    def __init__(self, path: str | Path):
        self.path = str(path)
        with sqlite3.connect(self.path) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("CREATE TABLE IF NOT EXISTS consumed(authority_id TEXT PRIMARY KEY, consumed_at REAL DEFAULT (unixepoch('subsec')))")
    def consume_once(self, authority_id: str) -> bool:
        try:
            with sqlite3.connect(self.path, timeout=5.0) as c:
                c.execute("INSERT INTO consumed(authority_id) VALUES (?)", (authority_id,))
            return True
        except sqlite3.IntegrityError:
            return False
    def is_used(self, authority_id: str) -> bool:
        with sqlite3.connect(self.path) as c:
            return c.execute("SELECT 1 FROM consumed WHERE authority_id=?", (authority_id,)).fetchone() is not None
