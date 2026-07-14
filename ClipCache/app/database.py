import sqlite3
import time
from pathlib import Path
from typing import Optional


DB_PATH = Path.home() / ".clipcache" / "clipcache.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            pinned INTEGER NOT NULL DEFAULT 0,
            created_at REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_items_pinned ON items(pinned DESC)
    """)
    conn.commit()
    conn.close()


def add_item(content: str) -> Optional[int]:
    """Add a new clipboard item. Returns the id, or None if duplicate of latest."""
    conn = get_connection()
    # Don't add if it's identical to the most recent unpinned item
    row = conn.execute(
        "SELECT content FROM items WHERE pinned = 0 ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if row and row[0] == content:
        conn.close()
        return None
    cursor = conn.execute(
        "INSERT INTO items (content, pinned, created_at) VALUES (?, 0, ?)",
        (content, time.time()),
    )
    item_id = cursor.lastrowid
    conn.commit()
    # Trim old unpinned items (keep max 500)
    _trim_old()
    conn.close()
    return item_id


def _trim_old():
    conn = get_connection()
    conn.execute("""
        DELETE FROM items WHERE pinned = 0 AND id NOT IN (
            SELECT id FROM items WHERE pinned = 0 ORDER BY created_at DESC LIMIT 500
        )
    """)
    conn.commit()
    conn.close()


def search_items(query: str = "", limit: int = 100, pinned_only: bool = False) -> list[dict]:
    """Search clipboard history. Empty query returns all (pinned first)."""
    conn = get_connection()
    if pinned_only:
        if query:
            rows = conn.execute(
                """SELECT id, content, pinned, created_at FROM items
                   WHERE pinned = 1 AND content LIKE ?
                   ORDER BY created_at DESC LIMIT ?""",
                (f"%{query}%", limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, content, pinned, created_at FROM items
                   WHERE pinned = 1 ORDER BY created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
    else:
        if query:
            rows = conn.execute(
                """SELECT id, content, pinned, created_at FROM items
                   WHERE content LIKE ? ORDER BY pinned DESC, created_at DESC LIMIT ?""",
                (f"%{query}%", limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, content, pinned, created_at FROM items
                   ORDER BY pinned DESC, created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
    conn.close()
    return [
        {"id": r[0], "content": r[1], "pinned": bool(r[2]), "created_at": r[3]}
        for r in rows
    ]


def toggle_pin(item_id: int) -> bool:
    """Toggle pinned status. Returns new pinned state."""
    conn = get_connection()
    conn.execute("UPDATE items SET pinned = 1 - pinned WHERE id = ?", (item_id,))
    row = conn.execute("SELECT pinned FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.commit()
    conn.close()
    return bool(row[0]) if row else False


def delete_item(item_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM items WHERE id = ? AND pinned = 0", (item_id,))
    conn.commit()
    conn.close()


def clear_history():
    """Delete all unpinned items."""
    conn = get_connection()
    conn.execute("DELETE FROM items WHERE pinned = 0")
    conn.commit()
    conn.close()


def export_pinned() -> list[dict]:
    """Export all pinned items as a list."""
    return search_items("", limit=1000, pinned_only=True)


def import_pinned(items: list[dict]):
    """Import pinned items from a list. Skips duplicates."""
    conn = get_connection()
    now = time.time()
    imported = 0
    for item in items:
        content = item.get("content", "")
        if not content:
            continue
        # check if already exists (avoid dupes)
        existing = conn.execute(
            "SELECT id FROM items WHERE content = ? AND pinned = 1 LIMIT 1",
            (content,),
        ).fetchone()
        if existing:
            continue
        conn.execute(
            "INSERT INTO items (content, pinned, created_at) VALUES (?, 1, ?)",
            (content, now),
        )
        imported += 1
        now += 0.001  # space them out a bit
    conn.commit()
    conn.close()
    return imported


def count_items() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    pinned = conn.execute("SELECT COUNT(*) FROM items WHERE pinned = 1").fetchone()[0]
    conn.close()
    return {"total": total, "pinned": pinned}
