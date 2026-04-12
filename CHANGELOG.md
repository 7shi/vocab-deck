# VocabDeck – Changelog

<!--
Policy:
- One section per date; prepend new items at the top of the section (newest first).
- CHANGELOG records what changed and why (history). README describes the current design (reference).
  Detailed rationale, implementation specifics, and "replaced X with Y" language belong here, not in README.
- Entries invalidated by a later implementation are moved to CHANGELOG.obsolete.md with a note explaining which change superseded them.
-->

## v0.1.1 (2026-04-13)

- **Fix: language suffix stripped from deck title**: `make_title()` and the `list_tomls()` topic extractor previously only stripped `-orig`-suffixed language tags (e.g. `.ja-orig`). Plain language suffixes (e.g. `.en`, `.ja`) were left in the title, producing names like "Penrose Quantum.En". The regex `\.[a-z]{2,3}-orig$` is now `\.[a-z]{2,3}(-orig)?$` so both forms are removed.

## v0.1.0 (2026-03-09)

- **Packaged as `vocab-deck` 0.1.0**: The project is now a proper Python package using hatchling as the build backend. `vocab_deck/` gained `__init__.py` (exposes `__name__ = "vocab-deck"` and `__version__` via `importlib.metadata`) and `__main__.py` (enables `python -m vocab_deck`). All intra-package imports converted from bare to relative (`from .module import …`). A `[project.scripts]` entry adds the `vocab-deck` console script (`uv run vocab-deck`). A `--version` flag prints the package name and version from metadata.

## 2026-03-08

- **Run from the current working directory by default**: The app no longer assumes vocab TOML files live in the parent directory of `flashcard/`. Runtime path handling is now centralized, and the default data root is the process current working directory (`Path.cwd()`). `helpers.py` no longer uses a fixed `Path(__file__).parent.parent`; `list_tomls()` and `load_words()` instead read from the configured data directory. A new `--data-dir PATH` CLI option overrides the default when needed.

- **Shared app state moved under `~/.config/vocab-deck/`**: Persistent settings and the default memo database location are now resolved from the app config directory instead of local files in `flashcard/`. `settings.toml` now defaults to `~/.config/vocab-deck/settings.toml`, and `memo.db` now defaults to `~/.config/vocab-deck/memo.db`. `settings.py` and `memo.py` create parent directories automatically as needed. A new `--memo-db PATH` CLI option overrides the memo DB location without affecting the shared settings location.

- **Import-time DB initialization removed**: `memo.py` no longer creates the SQLite DB at import time. DB initialization now runs during app startup, after CLI options are parsed, so `--memo-db` is honored consistently even when the server is launched with a custom memo DB path.

- **External app name changed to `VocabDeck`**: User-facing naming was updated from the generic `Flashcard` label to `VocabDeck`. This includes the README title, the main library page title, the card-page back link label, the CLI description string, and the changelog headings. The runtime config directory name is now `vocab-deck`.

## 2026-02-22

- **Fix: TTS word highlight misses tokens split by `<strong>` tags**: `onboundary` previously found a single span by exact `data-start` match, so only the pre-`<strong>` fragment (e.g. `d'` in `d'<strong>ordre</strong>`) was highlighted. The handler now computes the word's end position — from `e.charLength` when available, otherwise by scanning for the next whitespace in the plain text — and highlights all spans whose `data-start` falls within `[charIndex, end)`.

- **Library list heading order changed to `[lang] date title`**: Each Library entry now displays the language badge, date, and topic in that order. Previously the title was `"Topic (YYYY-MM-DD)"` (topic first, date in parentheses). `list_tomls()` now also returns `date` (`YYYY-MM-DD` string, empty for files without a date prefix) and `topic` (topic part only, without date). `render_index()` inserts a `<span class="card-link-date">` between the lang badge and the title; the span is omitted when `date` is empty. A `.card-link-date` rule (12 px, muted color) is added to `index.css`. `make_title()` is unchanged and continues to be used for the card page `<title>` and `<h1>`.

## 2026-02-21

- **Language code badge in Library**: Each entry in the Library list now shows the BCP 47 language code (e.g. `hi-IN`) as a small badge to the left of the card count. Rendered as `<span class="card-link-lang">` to the left of the title, wrapped with it in `<span class="card-link-left">` (flex row); card count remains right-aligned in `card-link-meta`. Styled with a subtle border and background in `index.css`.

- **Library sort order**: `list_tomls()` now sorts by three levels — date extracted from the filename (`YYYYMMDD` prefix, newest first), file modification time (newest first), then filename (ascending). Files without a date prefix sort last (date treated as 0).

- **`[Ctrl]+[Enter]` works inside textareas**: `[Ctrl]+[Enter]` is now an alias for `[Enter]` (guided-play action) that fires even when a memo textarea is focused. The `keydown` guard (`if (e.target.tagName === 'TEXTAREA') return`) now passes through when `ctrlKey && key === 'Enter'`, allowing the review flow to continue without leaving the text field.

- **Clear AI suggestions on new generation**: Starting a new AI generation (hint or memo) now immediately removes the `open` class from both suggestion lists, hiding any previously shown candidates before the new results arrive.

- **Fix: hint edits on back face overwritten on navigation**: `flipCard()` updated `memo-hint-area` when flipping to back, but did not update `memo-front-area` when flipping to front. After flipping back to front, `memo-front-area` held a stale value; a subsequent `saveAllPending()` (e.g., on navigation) would read that stale value and write it back to the DB, overwriting the newer hint edited on the back face. Fixed by adding an `else` branch that sets `memo-front-area.value = memoMap[word]?.front` when flipping to front.

- **Cancel AI generation by clicking the active button**: The "✨ AI生成" buttons are no longer disabled during generation. Instead, an `aiGenerating` boolean flag guards re-entry. While generation is active, the active button shows "生成中..."; clicking either button calls `cancelAiGeneration()`, which resets both buttons and sends `POST /api/ai/cancel`. Click handlers route through `if (aiGenerating) cancelAiGeneration(); else aiGenerate…()`.

- **AI generation improves existing text**: When the hint textarea (front face) already contains text, `POST /api/ai/hint` now includes it as `hint` in the request, and `generate_hint` switches to an improvement prompt asking for refinements or alternative approaches based on the existing hint. Similarly, when the memo textarea (back face) already contains text, `POST /api/ai/memo` includes it as `memo`, and `generate_memo` switches to an improvement prompt. Both fall back to the original from-scratch prompts when the respective field is absent or empty.

- **Log on AI cancel**: `POST /api/ai/cancel` now prints `[ai] cancelled` to stdout when invoked, making it visible in the server log that a generation was interrupted.

- **`save_memo` skips INSERT for empty text**: If `text` is empty and no DB entry exists for `(lang, word, face)`, no row is created. If an entry already exists, it is updated to empty as before. Implemented by splitting the single `INSERT … ON CONFLICT DO UPDATE` into an `INSERT OR UPDATE` branch (non-empty) and an `UPDATE`-only branch (empty).

- **Memo DB key changed from `stem` to `lang`**: `memos` table primary key changed from `(stem, word, face)` to `(lang, word, face)`. Memos are now shared across all files of the same language, so the same word in two different files of the same language shows and saves the same memo. `load_memos` and `save_memo` now take `lang` (BCP 47 tag via `detect_lang()`) instead of `stem`; `server.py` derives `lang` from the stem before calling these functions. A standalone migration script `VocabDeck`'s `flashcard/migrate_memo.py` converts existing DBs: it renames the old table to `memos_v2`, creates the new schema, maps each row's `stem` to `lang` via `detect_lang()`, resolves duplicate `(lang, word, face)` keys by keeping the row with the latest `updated_at`, then drops `memos_v2`. Supports `--db PATH` and `--dry-run` options.

- **AI candidate selection saves immediately**: Clicking an AI-generated candidate in `showAiSuggestions` now calls `cancelAndSave(face)` directly instead of dispatching an `input` event, bypassing the 3-second debounce and saving to the DB instantly. The face is derived from `targetAreaId` (`memo-back-area` → `'back'`, otherwise `'front'`).

- **AI generation log stream via SSE**: During AI generation, progress is streamed to the browser via `GET /api/ai/log` (Server-Sent Events). `LLMClient` gains `_log_queue` (`asyncio.Queue`) and `_emit()`, which pushes each text chunk to the queue instead of printing to stdout. At the start of `chat()`, stale messages are drained from the queue; a `None` sentinel is placed in `finally` to signal completion. The SSE endpoint reads from the queue with a 60-second timeout and encodes each message as JSON. On the JS side, `openAiLog()` opens an `EventSource` and appends received text to `<div id="ai-log">`; `closeAiLog()` closes the connection and hides the element. Both are called from `aiGenerateHint()` / `aiGenerateMemo()` (open before fetch, close in finally) and from `cancelAiGeneration()`. Thinking content (`[ai] thinking...\n` + streamed CoT) and the structured-output JSON are displayed as they arrive. All `print()` calls in `ai.py` (including `generate_hint` / `generate_memo` preamble logs) were removed; logging now goes exclusively to the browser.

- **[Enter] cancels and advances during speech**: Pressing `[Enter]` while TTS is speaking now stops the utterance and immediately advances to the next step (flip to back, or next card), rather than stopping and requiring a second `[Enter]`. `spokeAfterTransition` is now set inside the `onstart` callback of `speakWith()` and `speakExample()` (when the browser actually begins speaking), instead of inside `startSpeak()` (when speech was merely requested). This means the flag correctly reflects that audible output has occurred; and since it is already `true` when the user presses `[Enter]` mid-speech, the `enterAction()` advance logic fires immediately after `stopSpeechInternal()` without an extra keypress.

- **AI hint generation**: A "✨ AI生成" button inside the front-face hint collapsible generates 5 sound-based Japanese mnemonic candidates for the current word via `POST /api/ai/hint`. The prompt instructs the model to connect the word's sound to Japanese words or phrases without mentioning the meaning (since the meaning is the answer). The word's `reading` field is included in the context to help local LLMs that may not reliably read the target script. Candidates are shown as a clickable list below the textarea; selecting one fills the textarea and triggers a debounced save.

- **AI memo generation**: A "✨ AI生成" button below the back-face memo textarea generates 5 hint-to-meaning connection candidates via `POST /api/ai/memo`. Requires a non-empty hint; if the hint is empty, focus is moved to the hint textarea instead. The prompt asks the model to derive the meaning from the hint.

- **`LLMClient` with async streaming and cancellation**: `ai.py` implements `LLMClient` wrapping `ollama.AsyncClient`. Generation uses `stream=True` so the event loop remains responsive. A `_cancelled` flag is checked after each chunk; setting it (via `cancel()`) aborts mid-stream and returns `None`. The HTTP client is closed in a `finally` block via `client._client.aclose()`. `keep_alive=-1` keeps the model resident in memory between requests. The server-side singleton `llm_client` is shared across requests; a new request implicitly supersedes the previous one.

- **`POST /api/ai/cancel` endpoint**: Calls `llm_client.cancel()`. The browser sends this when navigating or flipping the card, resetting the button state immediately. Cancelled generation returns HTTP 204; the JS skips showing suggestions on 204.

- **`-m/--model` CLI argument**: Overrides the default Ollama model (`gpt-oss:120b`) at startup. `ai.MODEL` is patched before the server starts.

- **Reading on card back**: The `reading` field is now displayed in the back-face header alongside the word, using a small italic style matching the front-face reading.

- **Hint collapsible default state**: On card navigation, the hint collapsible now opens automatically when the hint is empty (ready to enter a new hint) and starts closed when hint text already exists.

- **Memo blur save fix**: `cancelAndSave(face)` replaces `saveMemoNow(face)` in all `blur` handlers. On focus-out, the pending debounce timer is cancelled and the save fires immediately, preventing the timer from one textarea from overwriting a save triggered by the other.

## 2026-02-20

- **Indic bold expansion in `bold_to_html`**: For Indic-script languages (hi/kn/te/ta/ml/bn/mr/gu/pa/ur), `bold_to_html` now expands bold markers to the full space-delimited word(s) to prevent mid-glyph rendering breaks. For example, `**ab**c` becomes `<strong>abc</strong>` and `**abc de**f` becomes `<strong>abc def</strong>`. Applied to `example` only; `translation` is always Japanese and uses the default (no expansion). Language detection uses the `-orig` suffix in the file stem. A `test_helpers.py` was added covering both expand and non-expand paths.

- **[Enter] guided-play shortcut; auto-speak removed**: Added `[Enter]` as a
  step-wise guided shortcut. A `spokeAfterTransition` flag tracks whether
  speech has occurred since the last card navigation or flip. When the flag is
  clear, `[Enter]` speaks (face-aware: word on front, example on back); when
  set, `[Enter]` flips to the back (from front) or advances to the next card
  (from back). `[Space]` also sets the flag, so mixing `[Space]` and `[Enter]`
  works naturally. Pressing `[Enter]` while speaking stops speech without
  advancing; the next press resumes the decision. Auto-speak
  (`startSpeak(false)` in `renderCard()`) has been removed; cards now display
  silently unless speech is triggered by the user.

- **[Space] speak shortcut**: The TTS toggle shortcut was changed from `[Enter]` to `[Space]`. The kbd-hint on the 🔊 読み上げ button and the README shortcut table are updated accordingly.


- **Hint section always visible on back face**: The "ヒント" textarea on the back face is now always shown regardless of whether the hint text is empty. Previously it was hidden when empty and revealed on first input; now it renders unconditionally whenever the back face is displayed.

- **Front/back face-specific memos**: Memo storage redesigned from a single shared memo per word to separate front-face and back-face memos. The front face shows a collapsible "ヒントを見る▼" toggle button; clicking expands a textarea for entering hint text (on card navigation, reset to open if hint is empty, closed if hint has content — see 2026-02-21). The back face always shows the front memo as an editable "ヒント" textarea (edits save to `face='front'`) plus a separate "メモ" textarea for back-face annotations. Schema changed to `memos(stem, word, face, text, updated_at, PRIMARY KEY (stem, word, face))`; existing DBs are migrated automatically (old rows become `face='front'`). `GET /api/memo` now returns `{word: {front: text, back: text}}`; `POST /api/memo` now requires a `face` field (`'front'` | `'back'`). Navigation (buttons and keyboard) calls `saveAllPending()` before moving, flushing both faces immediately.

- **Keyboard hint separator convention**: Nav button kbd-hints now use `, ` between keys that perform the same action (← 前へ: `[←], [PgUp]`; 次へ →: `[→], [PgDn]`) and ` / ` between keys that perform opposite actions (フリップ: `[↑] / [↓]`). README shortcut table updated to match.

- **[Space] flip shortcut removed; フリップ button relabeled [↑][↓]**: `[Space]` no longer flips the card. The フリップ button kbd-hint is updated to `[↑][↓]`, reflecting that `[↑]` and `[↓]` are the keyboard flip shortcuts.

- **[↓][↑] seamless flip-and-navigate shortcuts**: `[↓]` advances through cards in sequence — front → back → next card's front → back → …. On the front face it flips to the back; on the back face it navigates to the next card. `[↑]` is the exact reverse: on the back face it flips to the front; on the front face it navigates to the previous card and immediately shows its back face. Implemented by adding a `startFlipped = false` parameter to `renderCard()`: when `true`, the back face is rendered and the card is set to flipped state directly without the flip-back animation.

- **Nav button order changed**: Reordered from ← 前へ / フリップ / 🔊 読み上げ / 次へ → to ← 前へ / 🔊 読み上げ / フリップ / 次へ →.

- **Nav button layout**: All nav buttons occupy equal fixed-width slots (`flex: 0 0 calc((100% - 32px) / 5); box-sizing: border-box`) sized for five buttons with 8 px gaps. The four current buttons are centered (`justify-content: center`); a fifth can be added without layout changes. `align-items: stretch` ensures equal height across buttons of differing content. Keyboard shortcut hints are embedded in each button label with `<br><small class="kbd-hint">`, replacing the former separate keyboard hints bar.
- **Flip button moved to nav; card text selectable**: Clicking the card scene no longer flips the card, enabling text selection and copy-paste inside the card. A "フリップ" button in the nav row toggles the flip.
- **Speech state machine**: Replaced the `speaking` boolean with a four-state machine (`idle | starting | speaking | stopping`). Pressing speak immediately transitions to `starting` and shows "停止" without waiting for `onstart`. Pressing stop transitions to `stopping` and defers the UI reset until `onerror` or `onend` fires. Clicks in `starting` or `stopping` states are ignored to prevent misfire on rapid taps. A `speechGeneration` counter is incremented on each new utterance; stale callbacks from previous utterances check the counter and return early, preventing race conditions during fast navigation.

- **Keyboard fix**: `keydown` handler now ignores events whose target is a `<textarea>`, so arrow keys and Space/Enter do not trigger card navigation while the memo field is focused.

- **PageUp / PageDown navigation**: `[PageUp]` and `[PageDown]` now navigate cards identically to `[←]` / `[→]`. Added to the on-screen keyboard hints.
- **Translation styling**: Removed `font-style: italic`. Bold parts (`<strong>`) now render in `#ffc844` (matching example bold color).
- **Bold support in translation**: `helpers.py` now passes `translation` through `bold_to_html()`, and `card.js` renders it with `innerHTML` instead of `textContent`.
- **Fix: next-card back face briefly visible when flipped**: When navigating while the card is showing its back face, `renderCard()` now updates only the front face first, triggers the flip-back animation, and defers the back face update to the `transitionend` event. A `pendingTransitionEnd` guard cancels any stale listener on rapid navigation.
- **Debug flag**: Added `const DEBUG = false;` at the top of `card.js`. All non-error `slog()` calls are now guarded by `if (DEBUG)`; only TTS `onerror` events log unconditionally.
- **Card back layout**: Moved the horizontal separator (`border-top`) from above the translation to above the example sentence, so the layout reads `<hr> example <br> translation` instead of `example <hr> translation`.
- **Word-level highlight during example TTS**: `speakExample()` uses the `onboundary` Web Speech API event to highlight the current word as it is spoken. Text nodes are tokenized in place with `TreeWalker`, wrapping each word in `<span class="word-token" data-start="N">` while preserving surrounding HTML (`<strong>` markup stays intact). The original HTML is restored on `onend`/`onerror`/`stopSpeech`.
- **Back face font sizes increased** (meaning unchanged at 28 px):
  - Word header: 18 px → 21 px
  - Notes: 13 px → 15 px
  - Example: 15 px → 17 px
  - Translation: 14 px → 16 px
