# Skill Design Know-How

Lessons learned from designing and operating LLM-driven skills (automated workflows), primarily through the development of the `vocab-toml` skill.

---

## 1. Validate LLM output with a script

### Background

LLM output is probabilistic — the same instruction can produce subtly different results on each run. Structural constraints required by a skill (field presence, format rules, etc.) are not reliably respected when left entirely to the LLM.

### Approach

Embed a validation step in the skill workflow: check the output file with a script after the LLM writes it.

```
LLM writes output → script validates → if errors, LLM fixes and rewrites → re-validate
```

### Distinguish errors from warnings

| Type | Description | Action |
|------|-------------|--------|
| **Error** | Clear rule violation (missing required field, forbidden pattern, etc.) | Must be fixed; re-run check |
| **Warning** | Judgment call needed (word match, inflected form, spelling variant, etc.) | Human or LLM inspects and decides |

Leaving warnings as a judgment call — rather than hard errors — avoids spurious corrections from over-detection.

### Validation script design guidelines

- Use exit code 0 (success) / 1 (failure) so the skill workflow can branch on the result.
- Error messages should identify the entry number, word name, and nature of the problem.
- Warnings should not increment the error count; output them in a way that prompts human review.

---

## 2. TOML is well-suited as an LLM output format

### Format comparison

| Format | Characteristics | LLM output stability |
|--------|-----------------|----------------------|
| JSON | Verbose (many quotes, commas, braces) | Missing commas and mismatched brackets are common |
| YAML | Structure expressed by indentation | Indentation errors cause parse failures |
| TSV | Simple, but tab output is unreliable | Tabs and spaces are easily mixed |
| **TOML** | Repeated structures via `[[table]]`; delimiters are explicit | Relatively stable |

### Use `[[word]]` array tables for repeated entries

Using the `[[table-name]]` syntax for repeated data means the LLM never has to manage sequential numbering.

```toml
# Bad: LLM must manage numbering
[word1_1]
[word1_2]

# Good: no numbering needed, just append
[[word]]
layer = 1
...

[[word]]
layer = 2
...
```

### Syntax validation is easy

Python 3.11+ standard library `tomllib` handles it directly.

```python
import tomllib
with open("output.toml", "rb") as f:
    data = tomllib.load(f)  # raises on syntax error
```

---

## 3. Prompt design tips

### Use a uniform field structure across all layers

Varying field behavior or meaning by layer destabilizes LLM output. Use the same field structure for every entry and represent "not applicable" with an empty string (`""`).

```
Bad:  omit example/translation for Layer 3 entries
Good: always output all 7 fields; use "" when the value is not needed
```

### Requiring bold in example sentences has a dual effect

Requiring `**word**` bold markup in the example field serves two purposes:

1. **Flashcard readability**: draws attention to the target word.
2. **Implicit self-check for the LLM**: to insert the bold marker, the LLM must choose a sentence that actually contains the target word.

### Use a different language for SKILL.md example data

If the sample output in `SKILL.md` uses the same language as the actual input, the LLM may be pulled toward reproducing the sample content. Use fictional data in a different language (e.g., Korean examples when the skill processes Kannada).

### How to phrase the no-truncation rule

Saying "verbatim sentence from source text" alone is not enough — the LLM will still truncate with `...`. Being explicit about the allowed simplification prevents this:

```
Bad:  "verbatim sentence from source text"
Good: "sentence from source text; may be simplified if too long, but never truncated with ..."
```

---

## 4. Skill directory structure

Place skill-specific scripts in a `scripts/` subdirectory of the skill directory.

```
skills/{skill-name}/
├── SKILL.md        # skill definition read by Gemini CLI
└── scripts/        # skill-specific scripts (optional)
    └── script.py
```

When a skill is active, the entire skill directory is added to the file-access allow-list, so scripts can be executed without being loaded into context (saves context window space).

Reference scripts from `SKILL.md` using a working-directory-relative path:

```
uv run skills/{skill-name}/scripts/script.py
```
