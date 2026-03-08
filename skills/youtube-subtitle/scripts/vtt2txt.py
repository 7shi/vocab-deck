import argparse
import os
import webvtt

parser = argparse.ArgumentParser(description="Convert VTT to plain text")
parser.add_argument("input", help="Input VTT file")
parser.add_argument("-o", "--output", help="Output text file (default: input with .txt extension)")
parser.add_argument("--url", help="Source URL to include in front matter")
parser.add_argument("--title", help="Video title to include in front matter")
args = parser.parse_args()

output = args.output or os.path.splitext(args.input)[0] + ".txt"

with open(output, "w", encoding="utf-8") as f:
    if args.url or args.title:
        f.write("---\n")
        if args.title:
            f.write(f"title: {args.title}\n")
        if args.url:
            f.write(f"url: {args.url}\n")
        f.write("---\n\n")
    prev = None
    for caption in webvtt.read(args.input):
        for line in caption.text.splitlines():
            line = line.strip()
            if line and line != prev:
                f.write(line + "\n")
                prev = line
