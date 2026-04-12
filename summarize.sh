#!/bin/sh
set -e
if [ "$1" = "-c" ]; then
    if [ -e _clip.tmp ]; then
        echo "エラー: _clip.tmp が既に存在します" >&2
        exit 1
    fi
    xsel --clipboard --output > _clip.tmp || { rm -f _clip.tmp; exit 1; }
    if [ ! -s _clip.tmp ]; then
        rm _clip.tmp
        echo "エラー: クリップボードが空です" >&2
        exit 1
    fi
    gemini --yolo -p "/clip-summarize _clip.tmp"
    LATEST=$(ls -t gemini/*.md 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        richmd "$LATEST"
    fi
elif [ -z "$1" ]; then
    echo "使用法: $0 [-c | target]" >&2
    exit 1
else
    TARGET=$1
    gemini --yolo -p "/article-summary-integrator $TARGET"
    richmd "gemini/$TARGET"
fi
