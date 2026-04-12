#!/bin/sh
set -e
if [ -z "$1" ]; then
    echo "使用法: $0 <YouTube-URL>"
    exit 1
fi
URL=$1

gemini --yolo -p "以下の手順を順に実行してください：
1. /youtube-subtitle $URL を実行して字幕を取得してください。ファイル名の接頭辞（PREFIX）の提案には自動で同意して進めてください。
2. 生成された字幕テキストファイルに対して /vocab-toml を実行してください。
3. 同じ字幕テキストファイルに対して /article-summary-integrator を実行してください。"

LATEST=$(ls -t gemini/*.md 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
    echo "$LATEST"
    richmd "$LATEST"
fi
