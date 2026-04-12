# VocabDeck – Design Decisions

Implementation decisions whose rationale is not evident from the code alone.

---

## Data storage

### SQLite for memo store (not JSON)
SQLite supports O(1) partial updates — one row per word — without reading or rewriting the full dataset. A JSON file would require loading and rewriting the entire object on every save, which is wasteful even at current data volumes and harder to make safe under concurrent writes.

### Memo DB key is `lang`, not `stem`
Memos are keyed by BCP 47 language tag (e.g. `en-US`) rather than by filename stem. This means the same word in two different deck files of the same language shares a single memo entry. The rationale: mnemonics and notes are properties of the word in a language, not of a particular deck file.

### DB initialization deferred to startup
`memo.py` does not create the SQLite DB at import time. Initialization runs after CLI options are parsed so that `--memo-db PATH` is honored consistently. Initializing at import time would silently use the default path even when a custom path was specified.

---

## File conventions

### Language code suffix in filename (`.en`, `.ja-orig`)
The language of a deck is encoded in the filename stem (e.g. `20260413-topic.en.toml`, `20260413-topic.ja-orig.toml`). The `-orig` suffix marks the source language of the original video; a plain code (`.en`) marks a translation. `detect_lang()` reads this suffix; without it, the app defaults to `en-US`.

---

## Runtime paths

### Data root is CWD, not the package directory
The app resolves TOML files relative to the process working directory (`Path.cwd()`), not relative to `vocab_deck/`. This lets users run `vocab-deck` from any directory containing their deck files without configuration. A `--data-dir` option overrides this when needed.

### Persistent state lives under `~/.config/vocab-deck/`
`settings.toml` and `memo.db` default to the XDG-style config directory rather than a project-local directory. This separates user data from the working directory so decks can be moved or checked out without losing memos or settings.

---

## LLM integration

### `LLMClient` is a singleton; new request implicitly supersedes the previous
A single `llm_client` instance is shared across all HTTP requests. Starting a new generation sets a `_cancelled` flag on any in-flight stream, which is checked after each chunk. There is no explicit queue: the assumption is that the user always wants only the most recent generation.

### `keep_alive=-1` for Ollama
Passing `keep_alive=-1` keeps the model loaded in GPU/CPU memory indefinitely between requests. Without this, Ollama unloads the model after each request and the next generation incurs a cold-load delay.

### AI log streamed via SSE, not printed to stdout
During generation, each text chunk is pushed to an `asyncio.Queue` and served to the browser over `GET /api/ai/log` (Server-Sent Events). Printing to stdout is not visible to users running the app from a desktop shortcut; SSE makes progress visible in the UI without a separate log window.

### Improvement prompt when text already exists
If the hint or memo textarea is non-empty when the user clicks "AI生成", the request includes the existing text and the prompt switches to "improve or offer alternatives" mode. This avoids throwing away work the user has already done.

### Candidate selection saves immediately (bypasses debounce)
Clicking an AI-generated candidate calls `cancelAndSave()` directly, skipping the normal 3-second debounce. The debounce exists to avoid write amplification during continuous typing; a deliberate candidate selection is a discrete event that should persist without delay.

### `save_memo` skips INSERT for empty text
If `text` is empty and no DB row exists for `(lang, word, face)`, no row is created. This prevents the DB from accumulating empty rows for every word the user visits without writing a note.

---

## UI and speech

### Four-state speech machine (`idle | starting | speaking | stopping`)
A boolean `speaking` flag was insufficient because browser TTS is asynchronous: `speak()` returns immediately but `onstart` fires later. Without intermediate states, rapid button taps caused mismatched stop/start events. The four-state machine ensures that clicks during `starting` or `stopping` are ignored and that stale `onstart`/`onend` callbacks from superseded utterances are detected and discarded via a `speechGeneration` counter.

### Indic bold expansion in `bold_to_html`
For Indic-script languages, `**bold**` markers are expanded to the full space-delimited word(s) rather than the exact marked span. Indic scripts use ligatures and conjunct consonants: wrapping a partial akshara sequence in `<strong>` causes the browser to render the glyphs independently, breaking the intended ligature. Expanding to word boundaries avoids splitting any ligature cluster.
