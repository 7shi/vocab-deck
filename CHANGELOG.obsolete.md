# VocabDeck – Obsolete Changelog Entries

<!--
Entries moved here were made invalid by a later implementation.
Each entry notes which later change superseded it.
-->

## 2026-02-20

- **Auto-speak on card display**: `renderCard()` now calls `speak()` at the end, so the front-face word is read aloud automatically whenever the card advances.
  → **Superseded by "[Enter] guided-play shortcut; auto-speak removed"**: `renderCard()` no longer calls `startSpeak()`; cards display silently unless speech is triggered by the user.

- **Per-card memo annotations**: A textarea below the navigation buttons lets users attach free-text notes to each card. Memos are shared between the front and back face and persist across sessions in `~/.config/vocab-deck/memo.db` (SQLite). Writes are debounced: changes are queued and flushed 3 seconds after the last keystroke. Navigating away from a card (button click or focus change) triggers an immediate save via the `blur` event, cancelling the pending timer. This prevents redundant writes during continuous typing while guaranteeing no data loss on card navigation.
  → **Superseded by "Front/back face-specific memos"**: memos are no longer shared between faces; the front face has a collapsible hint textarea and the back face has separate hint and memo textareas.

- **SQLite memo store** (`memo.py`): New module wrapping `sqlite3`. Schema: `memos(stem TEXT, word TEXT, text TEXT, updated_at TEXT, PRIMARY KEY (stem, word))`. Uses `INSERT … ON CONFLICT … DO UPDATE` for atomic upsert. SQLite is chosen over JSON because it supports O(1) partial updates (one row per word) without reading or rewriting the full dataset — appropriate even though current data volumes are small.
  → **Superseded by "Front/back face-specific memos"**: schema changed to `PRIMARY KEY (stem, word, face)` with `face TEXT NOT NULL DEFAULT 'front'`.

- **New API routes**: `GET /api/memo?f=<stem>` returns all memos for a file as `{word: text}`; `POST /api/memo` saves `{stem, word, text}`. Memos are fetched in parallel with settings and word data at page load.
  → **Superseded by "Front/back face-specific memos"**: `GET /api/memo` now returns `{word: {front: text, back: text}}`; `POST /api/memo` now requires `face` field.

- **Keyboard shortcut change**: Manual speak moved from `[S]` to `[Enter]`. `[Space]` retains flip. `[Enter]` is face-aware: front → speak word, back → speak example sentence.
  → **Fully superseded**: first by "[Space] flip shortcut removed" (`[Space]` no longer flips), then by "[Space] speak shortcut" (`[Space]` is now the speak shortcut), then by "[Enter] guided-play shortcut; auto-speak removed" (`[Enter]` now runs the guided review flow instead of acting as the manual speak key).

- **Speak button consolidated to nav**: Removed the separate speak buttons from the front and back card faces. A single face-aware button in the nav row reads the word when the front is shown and the example sentence when the back is shown. `[Enter]` behaves identically.
  → **Superseded by "[Space] speak shortcut" and "[Enter] guided-play shortcut; auto-speak removed"**: the nav speak button remains, but the keyboard behavior changed so manual speech is on `[Space]` and `[Enter]` now advances the guided review flow.

- **Keyboard fix: button focus no longer steals shortcuts**: The `keydown` handler previously returned early when `e.target` was a `<button>`, causing all shortcuts to silently fail after clicking any nav button. The guard is removed; instead, if a button has focus the handler calls `e.target.blur()` before the switch statement. `e.preventDefault()` on `[Enter]` prevents the focused button from being inadvertently activated.
  → **Partially superseded by "[Space] speak shortcut"**: the key whose default action must be suppressed changed from `[Enter]` to `[Space]`. The underlying fix for button focus still applies.

- **Example sentence TTS**: Added a speak button at the bottom of the card back face. Tapping it (or pressing `[Enter]` while on the back) reads the example sentence aloud using the cached working voice.
  → **Superseded by "Speak button consolidated to nav"**: the per-face speak buttons (front and back) were removed and replaced by a single face-aware button in the nav row.
