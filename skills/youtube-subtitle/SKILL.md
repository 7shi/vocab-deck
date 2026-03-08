---
name: youtube-subtitle
description: Downloads the original-language subtitle from a YouTube video, converts it to plain text, and saves it with an auto-generated filename (YYYYMMDD-xxx-yyy). Use when given a YouTube URL and asked to download subtitles.
---

# YouTube Subtitle Downloader

## Purpose
Download the original-language subtitle of a YouTube video, convert it from VTT to plain text, and save it with a consistent filename.

## Arguments
- **`url`** (required): YouTube video URL

## Workflow
1. **Get title**: Run `yt-dlp --print title [url]`
2. **Get date**: Run `date +%Y%m%d`
3. **Generate PREFIX**: Compress the title to 2 English lowercase words → `YYYYMMDD-xxx-yyy`
4. **Confirm with user**: Show the proposed PREFIX and ask for approval before proceeding
5. **Download subtitle**: `yt-dlp --write-auto-subs --sub-langs ".*-orig" --skip-download -o "PREFIX.%(ext)s" [url]`
6. **Convert to text**: `uv run .gemini/skills/youtube-subtitle/scripts/vtt2txt.py PREFIX.<lang>-orig.vtt --url [url] --title [title]`
   - `<lang>` is the language code detected in the downloaded filename (e.g. `kn`)
   - `[title]` is the title obtained in step 1

## Notes
- The `.*-orig` pattern matches the original-language auto-caption (e.g. `kn-orig` for Kannada)
- VTT and TXT files are saved in the current directory
