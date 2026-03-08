#!/bin/sh
if [ -z "$1" ]; then
    echo "使用法: $0 target"
    exit 1
fi
TARGET=$1
gemini --yolo -p "article-summary-integrator $TARGET"
richmd "gemini/$TARGET"
