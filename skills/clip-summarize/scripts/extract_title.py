#!/usr/bin/env python3
"""Extract title from YAML Front Matter of a file."""
import re
import sys


def extract_title(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---\n"):
        print("エラー: YAML Front Matterが見つかりません", file=sys.stderr)
        sys.exit(1)

    end = content.find("\n---", 4)
    if end == -1:
        print("エラー: YAML Front Matterが閉じられていません", file=sys.stderr)
        sys.exit(1)

    front_matter = content[4:end]
    for line in front_matter.splitlines():
        m = re.match(r"^title:\s*(.+)$", line)
        if m:
            title = m.group(1).strip().strip("\"'")
            print(title)
            return

    print("エラー: titleフィールドが見つかりません", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"使用法: {sys.argv[0]} <file>", file=sys.stderr)
        sys.exit(1)
    extract_title(sys.argv[1])
