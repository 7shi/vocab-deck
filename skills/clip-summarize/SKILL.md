---
name: clip-summarize
description: Extracts the title from a clipboard dump file's YAML Front Matter, generates a date-prefixed slug, renames the file to slug.md, and summarizes it using article-summary-integrator. Use when given a clipboard dump file to summarize.
---

# Clip Summarize

## Purpose
Process a clipboard dump file: extract the title via a bundled script, generate a slug, rename the file, and produce a Japanese summary via article-summary-integrator.

## Arguments
- **`input_file`** (required): Path to the clipboard dump file (e.g., `_clip.tmp`)

## Workflow
1. **Extract title**: Run `uv run skills/clip-summarize/scripts/extract_title.py [input_file]`
   - On success: stdout contains the title; proceed
   - On error: stderr contains the error message; report it and stop
2. **Get date**: Run `date +%Y%m%d`
3. **Generate slug**: Compress the title to 2 English lowercase words → `YYYYMMDD-xxx-yyy`
4. **Check for conflict**: If `YYYYMMDD-xxx-yyy.md` already exists, extend to 3 words → `YYYYMMDD-xxx-yyy-zzz`
5. **Confirm with user**: Show the proposed slug and ask for approval before proceeding
6. **Rename file**: Run `mv [input_file] SLUG.md`
7. **Summarize**: Use the `article-summary-integrator` skill with `input_file=SLUG.md`
