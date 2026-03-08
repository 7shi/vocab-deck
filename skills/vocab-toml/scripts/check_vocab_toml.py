#!/usr/bin/env python3
"""Structural checker for vocab-toml output files."""

import re
import sys
import tomllib
from pathlib import Path

REQUIRED_FIELDS = {"layer", "word", "reading", "meaning", "notes", "example", "translation"}


def check(path: Path) -> int:
    errors = 0

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"TOML parse error: {e}")
        return 1

    words = data.get("word", [])
    if not words:
        print("No [[word]] entries found")
        return 1

    layer_counts = {1: 0, 2: 0, 3: 0}

    for i, entry in enumerate(words, 1):
        label = f"entry {i} ({entry.get('word', '?')})"

        # Required fields
        missing = REQUIRED_FIELDS - entry.keys()
        if missing:
            print(f"{label}: missing fields: {missing}")
            errors += 1

        # layer value
        layer = entry.get("layer")
        if layer not in (1, 2, 3):
            print(f"{label}: invalid layer={layer!r}")
            errors += 1
        else:
            layer_counts[layer] += 1

        # String fields
        for field in REQUIRED_FIELDS - {"layer"}:
            if field in entry and not isinstance(entry[field], str):
                print(f"{label}: {field} must be a string")
                errors += 1

        example = entry.get("example", "")
        word = entry.get("word", "")

        # Bold markers in example
        if "**" not in example:
            print(f"{label}: example has no bold markers (**)")
            errors += 1
        else:
            # Warn if bolded text doesn't look related to word (inflection allowed)
            bolded_texts = re.findall(r"\*\*(.+?)\*\*", example)
            bolded = " ".join(bolded_texts)
            if not (word in bolded or bolded in word or
                    bolded.startswith(word) or word.startswith(bolded)):
                print(f"  Warning: bold={bolded!r} may not match word={word!r}")

        # No ellipsis
        if "..." in example:
            print(f"{label}: example contains '...' (truncation not allowed)")
            errors += 1

        # Layer 3: notes should not be empty
        if layer == 3 and entry.get("notes") == "":
            print(f"{label}: Layer 3 notes is empty (should describe the proper noun)")
            errors += 1

    # Layer count summary
    total = sum(layer_counts.values())
    print(f"Entries: Layer 1={layer_counts[1]}, Layer 2={layer_counts[2]}, Layer 3={layer_counts[3]}  (total={total})")
    if not (8 <= layer_counts[1] <= 12):
        print(f"Warning: Layer 1 count={layer_counts[1]} (expected ~10)")
    if not (8 <= layer_counts[2] <= 12):
        print(f"Warning: Layer 2 count={layer_counts[2]} (expected ~10)")

    if errors == 0:
        print("OK: no errors found")
    else:
        print(f"{errors} error(s) found")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} FILE.toml")
        sys.exit(1)
    sys.exit(check(Path(sys.argv[1])))
