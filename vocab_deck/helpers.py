import re
import tomllib
from pathlib import Path

from .config import get_config

LANGUAGE_MAP = {
    "hi": "hi-IN",
    "kn": "kn-IN",
    "te": "te-IN",
    "ta": "ta-IN",
    "ml": "ml-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "pa": "pa-IN",
    "ur": "ur-PK",
    "ko": "ko-KR",
    "ja": "ja-JP",
    "zh": "zh-CN",
    "fr": "fr-FR",
    "de": "de-DE",
    "es": "es-ES",
    "pt": "pt-BR",
    "ru": "ru-RU",
    "ar": "ar-SA",
    "id": "id-ID",
}


def detect_lang(stem: str) -> str:
    """Detect BCP 47 language tag from file stem."""
    match = re.search(r"\.([a-z]{2,3})-orig$", stem)
    if match:
        lang_code = match.group(1)
        return LANGUAGE_MAP.get(lang_code, lang_code)
    return "en-US"


def make_title(stem: str) -> str:
    """Generate a human-readable title from file stem."""
    base = re.sub(r"\.[a-z]{2,3}-orig$", "", stem)
    parts = base.split("-", 1)
    if len(parts) == 2 and re.match(r"^\d{8}$", parts[0]):
        date, topic = parts
        date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        topic_fmt = topic.replace("-", " ").title()
        return f"{topic_fmt} ({date_fmt})"
    return base.replace("-", " ").title()


INDIC_LANGS = {"hi", "kn", "te", "ta", "ml", "bn", "mr", "gu", "pa", "ur"}


def bold_to_html(text: str, expand_word: bool = False) -> str:
    """Convert **...** markdown bold to <strong> HTML.

    If expand_word is True (Indic scripts), bold is expanded to the full
    space-delimited word to avoid mid-glyph rendering breaks.
    E.g. '**ab**c def' → '<strong>abc</strong> def'.
    """
    if not expand_word:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    result = []
    i = 0
    while i < len(text):
        m = re.search(r"\*\*(.+?)\*\*", text[i:])
        if not m:
            result.append(text[i:])
            break
        abs_start = i + m.start()
        abs_end = i + m.end()

        # Expand to full space-delimited word
        word_start = abs_start
        while word_start > 0 and text[word_start - 1] not in " \n\t":
            word_start -= 1
        word_end = abs_end
        while word_end < len(text) and text[word_end] not in " \n\t":
            word_end += 1

        result.append(text[i:word_start])
        word_clean = re.sub(r"\*\*", "", text[word_start:word_end])
        result.append(f"<strong>{word_clean}</strong>")
        i = word_end

    return "".join(result)


def validate_stem(stem: str) -> bool:
    """Validate stem to prevent path traversal attacks."""
    return bool(re.match(r"^[\w.\-]+$", stem)) and ".." not in stem


def load_words(stem: str) -> list[dict]:
    """Load and process words from TOML file."""
    path = _resolve_toml_path(stem)
    if not path.exists():
        raise FileNotFoundError(f"{stem}.toml not found")
    with open(path, "rb") as f:
        data = tomllib.load(f)
    raw = data.get("word", [])
    lang_match = re.search(r"\.([a-z]{2,3})-orig$", stem)
    expand_word = bool(lang_match and lang_match.group(1) in INDIC_LANGS)
    return [
        {
            "layer": w.get("layer", 1),
            "word": w.get("word", ""),
            "reading": w.get("reading", ""),
            "meaning": w.get("meaning", ""),
            "notes": w.get("notes", ""),
            "example": bold_to_html(w.get("example", ""), expand_word),
            "translation": bold_to_html(w.get("translation", "")),
        }
        for w in raw
    ]


def list_tomls() -> list[dict]:
    """List TOML files that have [[word]] entries."""
    result = []
    toml_root = get_config().data_dir

    def _sort_key(p):
        m = re.match(r'^(\d{8})', p.stem)
        date = int(m.group(1)) if m else 0
        return (-date, -p.stat().st_mtime, p.stem)

    for path in sorted(toml_root.glob("*.toml"), key=_sort_key):
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            if not data.get("word"):
                continue
            stem = path.stem
            base = re.sub(r"\.[a-z]{2,3}-orig$", "", stem)
            parts = base.split("-", 1)
            if len(parts) == 2 and re.match(r"^\d{8}$", parts[0]):
                d = parts[0]
                date_fmt = f"{d[:4]}-{d[4:6]}-{d[6:]}"
                topic = parts[1].replace("-", " ").title()
            else:
                date_fmt = ""
                topic = base.replace("-", " ").title()
            result.append({
                "stem": stem,
                "title": make_title(stem),
                "date": date_fmt,
                "topic": topic,
                "count": len(data["word"]),
                "lang": detect_lang(stem),
            })
        except Exception:
            continue
    return result


def _resolve_toml_path(stem: str) -> Path:
    data_dir = get_config().data_dir
    path = (data_dir / f"{stem}.toml").resolve()
    if path.parent != data_dir:
        raise FileNotFoundError(f"{stem}.toml not found")
    return path
