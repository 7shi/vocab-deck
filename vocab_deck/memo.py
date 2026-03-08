import sqlite3

from .config import get_config


def _conn() -> sqlite3.Connection:
    db_path = get_config().memo_db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='memos'"
        ).fetchone()
        if not tables:
            conn.execute("""CREATE TABLE memos (
                lang TEXT NOT NULL,
                word TEXT NOT NULL,
                face TEXT NOT NULL DEFAULT 'front',
                text TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (lang, word, face)
            )""")


def load_memos(lang: str) -> dict[str, dict[str, str]]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT word, face, text FROM memos WHERE lang = ?", (lang,)
        ).fetchall()
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        if row["word"] not in result:
            result[row["word"]] = {}
        result[row["word"]][row["face"]] = row["text"]
    return result


def save_memo(lang: str, word: str, face: str, text: str) -> None:
    with _conn() as conn:
        if text:
            conn.execute("""
                INSERT INTO memos (lang, word, face, text, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                ON CONFLICT(lang, word, face) DO UPDATE SET
                    text = excluded.text, updated_at = excluded.updated_at
            """, (lang, word, face, text))
        else:
            conn.execute("""
                UPDATE memos SET text = '', updated_at = datetime('now')
                WHERE lang = ? AND word = ? AND face = ?
            """, (lang, word, face))
