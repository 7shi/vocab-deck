#!/usr/bin/env python3
"""Migration script: memo DB (stem, word, face) → (lang, word, face).

Usage:
    # Preview changes without writing
    uv run flashcard/migrate_memo.py --dry-run

    # Backup and migrate
    cp flashcard/memo.db flashcard/memo.db.bak
    uv run flashcard/migrate_memo.py
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# Allow importing helpers from the flashcard package
sys.path.insert(0, str(Path(__file__).parent))
from .config import default_config
from .helpers import detect_lang


def migrate(db_path: Path, dry_run: bool) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Check that the old schema exists
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "memos" not in tables:
        print("No 'memos' table found — nothing to migrate.")
        conn.close()
        return

    cols = {row[1] for row in conn.execute("PRAGMA table_info(memos)").fetchall()}
    if "lang" in cols:
        print("Table already uses 'lang' column — already migrated.")
        conn.close()
        return
    if "stem" not in cols:
        print("Unexpected schema: neither 'stem' nor 'lang' column found.", file=sys.stderr)
        conn.close()
        sys.exit(1)

    # Read all old rows
    rows = conn.execute(
        "SELECT stem, word, face, text, updated_at FROM memos"
    ).fetchall()

    # Convert stem → lang, resolve duplicates.
    # Rows with empty text are skipped entirely; among non-empty rows, latest updated_at wins.
    # Key: (lang, word, face) → (text, updated_at)
    merged: dict[tuple[str, str, str], tuple[str, str]] = {}
    for row in rows:
        if not row["text"]:
            continue
        lang = detect_lang(row["stem"])
        key = (lang, row["word"], row["face"])
        existing = merged.get(key)
        if existing is None or row["updated_at"] > existing[1]:
            merged[key] = (row["text"], row["updated_at"])

    if dry_run:
        print(f"-- dry-run: {len(rows)} rows → {len(merged)} rows after merge --")
        for (lang, word, face), (text, updated_at) in sorted(merged.items()):
            preview = text[:60].replace("\n", "\\n")
            print(f"  lang={lang!r} word={word!r} face={face!r} updated_at={updated_at!r} text={preview!r}")
        conn.close()
        return

    # Perform migration inside a transaction
    try:
        with conn:
            conn.execute("ALTER TABLE memos RENAME TO memos_v2")
            conn.execute("""CREATE TABLE memos (
                lang TEXT NOT NULL,
                word TEXT NOT NULL,
                face TEXT NOT NULL DEFAULT 'front',
                text TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (lang, word, face)
            )""")
            conn.executemany(
                "INSERT INTO memos (lang, word, face, text, updated_at) VALUES (?, ?, ?, ?, ?)",
                [
                    (lang, word, face, text, updated_at)
                    for (lang, word, face), (text, updated_at) in merged.items()
                ],
            )
            conn.execute("DROP TABLE memos_v2")
        print(f"Migration complete: {len(rows)} rows → {len(merged)} rows.")
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        conn.close()
        sys.exit(1)

    conn.close()


def main() -> None:
    default_db = default_config().memo_db_path
    parser = argparse.ArgumentParser(description="Migrate memo DB from (stem, word, face) to (lang, word, face)")
    parser.add_argument("--db", type=Path, default=default_db, help=f"DB path (default: {default_db})")
    parser.add_argument("--dry-run", action="store_true", help="Show conversion result without writing")
    args = parser.parse_args()

    if not args.db.exists():
        print(f"DB not found: {args.db}", file=sys.stderr)
        sys.exit(1)

    migrate(args.db, args.dry_run)


if __name__ == "__main__":
    main()
