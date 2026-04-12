---
name: vocab-toml
description: Reads a subtitle text file and extracts vocabulary using a 3-layer priority model, then outputs a TOML file with [[word]] array tables for flashcard creation. Use when given a subtitle text file and asked to extract vocabulary for language learning.
---

# Vocabulary Extractor to TOML

## Purpose
Analyze a subtitle/transcript text file and extract key vocabulary using a 3-layer priority model,
then save the result as a TOML file for use with flashcard tools.

## Arguments
- **`input_file`** (required): Path to a subtitle text file (e.g., `20260219-kanipura-temple.kn-orig.txt`)

## 3-Layer Extraction Model

### Layer 1: High-frequency × High-semantic-density words (~10 words)
- Content words that appear **multiple times** in the text
- Exclude function words (particles, conjunctions, auxiliaries)
- Highest learning ROI — understanding these words unlocks the overall structure

### Layer 2: Domain-specific vocabulary (~10 words)
- Topic-critical terms even if low frequency
- Examples: ritual names, architectural terms, historical/mythological concepts
- Essential for understanding the subject matter

### Layer 3: Proper nouns (people, place names, deity names)
- People, places, deities, dynasties
- Include an example sentence from the source text (same as other layers)
- Use `notes` to explain who/what the proper noun refers to
- Goal: recognition, aided by context

## Fields per entry (identical structure for all layers)

| Field | Content |
|-------|---------|
| layer | 1, 2, or 3 |
| word | word in target language |
| reading | academic romanization with diacritics; `""` if the target language uses Latin script |
| meaning | brief Japanese meaning |
| notes | supplementary context (use `""` if not needed; for Layer 3, describe who/what this proper noun is) |
| example | sentence from source text containing the target word; correct transcription errors (spelling mistakes, misheard proper nouns) and add missing punctuation to produce educational-quality text; simplify if too long, but never truncate with `...`; wrap the target word (or its inflected form) in `**...**` |
| translation | Japanese translation of example; wrap the Japanese equivalent of the target word in `**...**` |

## Workflow
1. **Read input file**: Read the full content of `input_file`
2. **Detect language**: Infer from filename extension (e.g., `.kn-orig.txt` → Kannada)
3. **Extract Layer 1 words**: Identify ~10 high-frequency content words with high semantic density
4. **Extract Layer 2 words**: Identify ~10 domain-specific terms critical to the topic
5. **Extract Layer 3 proper nouns**: List people, places, deities, dynasties
6. **Find example sentences**: For every word (all layers), find a sentence from the source text that contains the target word; correct transcription errors (misspelled proper nouns, phonetic mishearings) and add missing punctuation; do not rewrite sentence structure; do not truncate with `...`; wrap the target word (or its corrected/inflected form) in `**...**`; in the `translation`, wrap the Japanese equivalent of the target word in `**...**`
7. **Determine output path**: Replace `.txt` with `.toml` in the input filename
8. **Write TOML**: Output all entries using `[[word]]` array-of-tables format
9. **Check**: Run `uv run skills/vocab-toml/scripts/check_vocab_toml.py OUTPUT.toml` and review the results:
   - **Errors** (missing fields, no bold, `...` in example, etc.): fix and rewrite the affected entries, then rerun the check until no errors remain
   - **Warnings** (bold/word mismatch): inspect each case — inflected forms and spelling variants in the source text are acceptable; fix only if the bold clearly targets the wrong word
10. **Report**: Show the output file path and entry counts per layer

## Output
- File: same path as input with `.txt` replaced by `.toml`
  - e.g., `20260219-kanipura-temple.kn-orig.txt` → `20260219-kanipura-temple.kn-orig.toml`

## Example TOML output

```toml
[[word]]
layer = 1
word = "절"
reading = "cheol"
meaning = "寺院"
notes = ""
example = "이 **절**은 신라 시대에 창건된 유서 깊은 사찰입니다"
translation = "この**寺院**は新羅時代に創建された由緒ある寺です"

[[word]]
layer = 2
word = "공양"
reading = "kongyang"
meaning = "供養・供え物"
notes = "仏教で神仏に食べ物や花を捧げる行為"
example = "매일 아침 **공양**을 올리는 것이 이 절의 오랜 전통입니다"
translation = "毎朝**供養**を行うことがこの寺院の長い伝統です"

[[word]]
layer = 3
word = "원효대사"
reading = "Weonhyo Taesa"
meaning = "元暁大師"
notes = "新羅時代の高名な僧侶。仏教の大衆化に尽力し、この寺院の開祖とされる"
example = "**원효대사**께서 이 절을 처음 세우셨다고 전해집니다"
translation = "**元暁大師**がこの寺院を最初に建立されたと伝えられています"
```

## Notes
- Example sentences must come from the source text and must contain the target word; correct transcription errors (misspelled words, misheard proper nouns) and add missing punctuation to reach educational-quality text, but do not rewrite sentence structure; simplify if too long, but never use `...` to truncate
- Bold the target word (or its inflected form as it appears in the sentence) using `**...**`; if inflected, the `**` markers may span only the stem or the whole inflected form — whichever is less disruptive to readability; in `translation`, bold the Japanese equivalent of the target word
- Layer 1 and Layer 2 together should total ~20 entries
- Layer 3 entries have no upper limit — include all significant proper nouns
- All 7 fields are always present in every entry (no layer-specific omissions)
- `notes` is `""` for most Layer 1 & 2 words; contains background explanation for Layer 3 proper nouns
- `reading` field uses academic transliteration with diacritics (e.g., `brahma kalasōtsava`, `devastāna`); set to `""` for Latin-script languages (e.g., French, Spanish, Indonesian)
