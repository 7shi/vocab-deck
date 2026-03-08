---
name: article-summary-integrator
description: Summarizes and integrates one or more source articles into a single Markdown file in the `gemini/` directory. Use when you need to consolidate information from multiple related files into a structured summary.
---

# Article Summary and Integration

## Purpose
Consolidate one or more source articles (provided as `input_file`) into a single integrated Markdown file within the `gemini/` directory to centralize related information.

## Arguments
- **`input_file`** (required): One or more source Markdown file paths to summarize and integrate (e.g., `20250716-llama4.md 20250716-llama4-reddit.md`).

## Workflow
1. **Read Source Articles**: Read each file specified in `input_file`.
2. **Summarize and Integrate**:
   - Extract key information, arguments, and conclusions from each file.
   - Merge them into a new, coherent Markdown file written in Japanese.
   - Remove redundancies and ensure a readable format.
3. **Determine Output Path** (auto-generated):
   - Use the format `gemini/YYYYMMDD-subject.md` derived from the input file names' date and topic.
4. **Save to `gemini/` Directory**: Write the result to the auto-generated path.

## Examples
- `input_file=20250716-llama4.md 20250716-llama4-reddit.md` → `gemini/20250716-llama4.md`
- `input_file=20250717-gemini-cli.md` → `gemini/20250717-gemini-cli.md`
- `input_file=20250717-worktrees.md` → `gemini/20250717-worktrees.md`
