# VocabDeck

VocabDeck is a flashcard application for vocabulary study, driven by `vocab-toml` TOML files.

For the underlying design philosophy and cognitive learning model, see [CONCEPTS.md](CONCEPTS.md).

## Usage

The intended workflow is to generate vocab TOML files from YouTube videos using `youtube.sh` (see [Content Creation Workflow](#content-creation-workflow)), then load them in the flashcard server for study.

```bash
uv run vocab-deck [--host 127.0.0.1] [--port 8000] [-m MODEL] [--data-dir PATH] [--memo-db PATH]
```

`-m/--model` specifies the Ollama model for AI generation (default: `gpt-oss:120b`). The model is kept resident in memory (`keep_alive=-1`) to avoid repeated load times.
`--data-dir` defaults to the current working directory, so the app reads vocab TOML files from wherever it is launched.
Shared app state is stored under `~/.config/vocab-deck/` by default; `--memo-db` overrides only the memo database path.

Then open `http://localhost:8000/` in a browser.

## Features

### Navigation

The nav row has four equal-width buttons. Keyboard shortcuts are shown in each button label.

| Key | Action |
|---|---|
| `[←]`, `[PageUp]` | Previous card |
| `[→]`, `[PageDown]` | Next card |
| `[↓]` | Front → back; back → next card |
| `[↑]` | Back → front; front → previous card's back |
| `[Space]` | Speak (face-aware toggle) |
| `[Enter]` | Guided: speak if not yet spoken, else flip/advance |

`[Enter]` is the primary key for working through the deck. It always performs the next step in the canonical review flow — speak the front, flip to the back, speak the back, advance to the next card — so a single repeated key is enough to review cards with TTS. Other shortcuts are for fine-grained control: `[↓]`/`[↑]` flip or navigate without speaking, `[Space]` speaks without advancing, and `[←]`/`[→]` jump freely. Mixing is natural — `[Space]` to speak sets the same flag that `[Enter]` checks, so a subsequent `[Enter]` skips straight to the next step.

`[Ctrl]+[Enter]` is an alias for `[Enter]` that also works when a memo textarea is focused, allowing the guided-play flow to continue without leaving the text field.

`[↓]` and `[↑]` provide a seamless front→back→next flow through the deck. Clicking anywhere on the card does not flip it, so text can be selected and copied.

### TTS (Text-to-Speech)

TTS uses the browser's [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API). Major languages are supported in Chrome with online voices, but Microsoft Edge covers a wider range of languages and is recommended for less common languages.

> **Note:** In Edge, online voices are not available until the browser's built-in Read Aloud feature has been used at least once on any webpage. After that, online voices become available to the Web Speech API.

The 🔊 読み上げ button (`[Space]`) is face-aware: on the front it reads the word; on the back it reads the example sentence, with word-level highlighting as it is spoken. Cards display silently; speech is triggered by the user.

If a voice fails silently, the app retries through all available voices for the language. The first working voice is remembered across page loads, so subsequent cards start without retrying.

### Memo Annotations

Below the nav buttons, two memo areas are displayed depending on the current face:

- **Front face**: A "ヒントを見る▼" toggle button with a collapsible textarea for hint text. The collapsible opens automatically when the hint is empty (ready to type), and starts closed when hint text already exists. A "✨ AI生成" button below the textarea generates 5 sound-based Japanese mnemonic candidates; clicking a candidate fills the textarea.
- **Back face**: An editable "ヒント" textarea showing the front-face memo (edits are saved as the front-face memo), followed by a "メモ" textarea for back-face annotations. A "✨ AI生成" button below the memo textarea generates 5 hint-to-meaning connection candidates (requires a non-empty hint).

AI generation is powered by a local LLM via [Ollama](https://ollama.com/). During generation, a log area appears below the memo section and streams progress in real time — including the model's chain-of-thought (thinking) when supported — so the user can see that work is in progress. The log disappears automatically when generation completes or is cancelled.

Memos are stored per face and persist across sessions. Changes are saved automatically (3-second debounce; focus-out cancels the timer and saves immediately). AI generation is cancelled automatically when navigating or flipping the card.

### Layer Filter and Shuffle

Buttons above the card filter by layer (L1–L3) or show all cards. 🔀 Shuffle randomizes the current set.

## Content Creation Workflow

Vocab TOML files are created from YouTube videos using a pipeline of [Gemini CLI](https://github.com/google-gemini/gemini-cli) skills and shell scripts. The skills in `skills/` must be installed into Gemini CLI beforehand.

> **Note:** The shell scripts are hardcoded to use Gemini CLI. To use them with Claude Code or another AI CLI, edit the scripts to invoke the appropriate command.

### Skills (`skills/`)

| Skill | Description |
|---|---|
| `youtube-subtitle` | Downloads the original-language auto-caption from a YouTube video, converts VTT to plain text, and saves it as `YYYYMMDD-xxx-yyy.<lang>-orig.txt`. Requires [yt-dlp](https://github.com/yt-dlp/yt-dlp). |
| `vocab-toml` | Reads a subtitle text file and extracts vocabulary using a 3-layer priority model (L1: high-frequency content words, L2: domain-specific terms, L3: proper nouns), then writes a `.toml` flashcard file |
| `article-summary-integrator` | Summarizes and integrates one or more Markdown/text files into a single Japanese summary saved under `gemini/` |
| `clip-summarize` | Extracts the title from a clipboard dump file's YAML Front Matter, generates a date-prefixed slug, renames the file, and summarizes it via `article-summary-integrator` |

See [SKILL-DESIGN.md](SKILL-DESIGN.md) for lessons learned from designing these skills.

### Shell Scripts

Both scripts require [Gemini CLI](https://github.com/google-gemini/gemini-cli) and [richmd](https://github.com/7shi/richmd). The `-c` option of `summarize.sh` additionally requires [xsel](https://github.com/kfish/xsel) for clipboard access.

| Script | Usage | Description |
|---|---|---|
| `youtube.sh` | `youtube.sh <YouTube-URL>` | Runs the full pipeline — `youtube-subtitle` → `vocab-toml` → `article-summary-integrator` — then displays the generated summary with `richmd`. |
| `summarize.sh` | `summarize.sh <target>` | Runs `article-summary-integrator` on an existing file and displays the result with `richmd`. |
| `summarize.sh` | `summarize.sh -c` | Reads clipboard content via `xsel`, runs `clip-summarize` to generate a slug and summarize, then displays the result with `richmd`. |

### Typical Workflow

```
youtube.sh <URL>
    ├─ youtube-subtitle   →  YYYYMMDD-xxx-yyy.<lang>-orig.txt
    ├─ vocab-toml         →  YYYYMMDD-xxx-yyy.<lang>-orig.toml   (flashcard source)
    └─ article-summary    →  gemini/YYYYMMDD-xxx-yyy.md          (study notes)
```

The generated `.toml` file can then be opened in the flashcard server.

## Developer Reference

Server code lives in `vocab_deck/`; frontend assets (CSS, JS) in `vocab_deck/static/`.

See [DECISIONS.md](DECISIONS.md) for implementation decisions whose rationale is not evident from the code alone.

### Routes

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Index page listing all vocab TOML files |
| `GET` | `/card?f=<stem>` | Flashcard UI for the given file stem |
| `GET` | `/api/words?f=<stem>` | Word data as JSON |
| `GET` | `/api/settings` | Current settings as JSON |
| `POST` | `/api/voice` | Save a working TTS voice for a language |
| `GET` | `/api/memo?f=<stem>` | All memos for a file as `{word: {front, back}}` |
| `POST` | `/api/memo` | Save a memo `{stem, word, face, text}` (`face`: `'front'`\|`'back'`) |
| `POST` | `/api/log` | Log a message from the browser to stdout |
| `POST` | `/api/ai/hint` | Generate hint candidates `{stem, word}` → `{items: [str×5]}` |
| `POST` | `/api/ai/memo` | Generate memo candidates `{stem, word, hint}` → `{items: [str×5]}` |
| `GET` | `/api/ai/log` | SSE stream of AI generation log (text chunks; `[DONE]` on completion) |
| `POST` | `/api/ai/cancel` | Cancel ongoing LLM generation |

The `f` parameter is the filename without the `.toml` extension (e.g. `20260219-south-north.hi-orig`). It is validated against `^[\w.\-]+$` to prevent path traversal.

### Settings File Format

`settings.toml` is written by the server to `~/.config/vocab-deck/settings.toml` by default and should not need manual editing, but it is human-readable:

```toml
[voice]
"hi-IN" = "Microsoft स्वरा Online (Natural) - Hindi (India)"
"kn-IN" = "Microsoft ಸಪ್ನಾ Online (Natural) - Kannada (India)"
```

Delete an entry to reset voice selection for that language.

### Debug Logging

`card.js` sends log messages to the server via `POST /api/log`, printed to stdout as `[browser] ...`. Set `const DEBUG = false;` to `true` in `card.js` to enable verbose logging. Only TTS errors are logged unconditionally.
