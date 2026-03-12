# Design Concepts of VocabDeck

VocabDeck is a system designed to support language acquisition by leveraging existing video content (e.g., YouTube) as learning material. This document outlines the underlying design philosophy and the cognitive pipeline used to transform unknown sounds into recognizable vocabulary.

## 1. Objective: Bridging Content and Language

The system is designed for learners who may not have immediate opportunities for conversation or travel but seek a practical connection to a language through authentic media.

*   **Authentic Content as a Gateway**: Language is inseparable from its cultural and historical context. By engaging directly with primary sources like narrations and documentaries, the learner establishes a practical interface with the language.
*   **Input-Centric Acquisition**: The focus is on auditory recognition and gradual vocabulary expansion. This allows learners to build background knowledge of history and culture concurrently with lexical growth.

## 2. Cognitive Load Management: The Warm-up Model

To facilitate a smooth transition to video viewing, vocabulary is filtered into a three-layer priority model. This "pre-processing" is designed to be completed in 5–10 minutes to maintain consistency.

*   **Layer 1**: High-frequency structural words (~10 words).
*   **Layer 2**: Domain-specific terms (e.g., history, geography) (~10 words).
*   **Layer 3**: Proper nouns (unlimited).

Strictly limiting Layers 1 and 2 prevents cognitive overload, ensuring the "warm-up" remains a sustainable routine rather than an exhaustive study session.

## 3. Data Generation Pipeline

The transformation of raw video into structured learning data is automated for efficiency.

*   **Extraction via Gemini CLI**: The system utilizes Gemini CLI for extracting key vocabulary from subtitles. Its generous rate limits for free-tier users make it suitable for processing large volumes of text.
*   **Automation Scripts**: Custom extensions and shell scripts handle the end-to-end workflow, from subtitle retrieval to TOML-formatted data generation.

## 4. Acquisition Pipeline: Auditory Anchoring and "Beachheads"

The flashcard deck employs a multi-step process to transform unknown sounds into meaningful units.

### Auditory Anchoring via TTS
Auditory exposure is the foundation. TTS (Text-to-Speech) is prioritized to ensure the "sound" of the language is established in the brain.
*   **Surface (Word)**: Displays the target word; TTS reads the word in isolation.
*   **Back (Example)**: Displays a sentence from the source video; TTS reads the sentence with real-time word-level highlighting. This allows learners to map sounds to scripts—even unfamiliar ones—without losing their place.

### Step 1: Sound Fixing (Phonetic Mnemonics)
Building a "beachhead" in an unknown language family is difficult. We use phonetic mnemonics (often called "Soramimi") to fix sounds.
*   **Mechanism**: Mapping an unknown sound to a known concept or sound in any familiar language. For example, the famous Japanese mnemonic for "What time is it now?" is *Hotta imo ijiruna* ("Don't touch the dug-up potatoes").
*   **Purpose**: The mnemonic result is less important than the process of ideation, which serves as a cognitive mechanism for repeated auditory exposure.

### Step 2: Provisional Bridging (Associative Memos)
Mnemonics serve as "training wheels" to connect fixed sounds to meanings. While these associations are provisional, they provide a necessary hook during the initial stages of recognition.

### Step 3: Meaning Establishment (Auditory Salience)
The back of the card provides context through example sentences. Learners are encouraged to practice "selective recognition"—identifying the target word within the sentence without necessarily parsing every other word. The goal is for words to "pop out" as meaningful units when the learner eventually watches the video.

## 5. Local LLM Integration

The ideation of mnemonics can be cognitively demanding. VocabDeck integrates local LLMs (via Ollama) to assist this process.
*   **Generative Support**: The LLM suggests multiple candidates for phonetic hints and associative memos.
*   **Friction Reduction**: Learners can select or modify these suggestions, significantly lowering the barrier to creating effective memory hooks.

## 6. From Context Engineering to Acquisition

This approach treats the warm-up as **Context Engineering for Inference** rather than a primary "Learning" (model update) event.
*   **Inference-time Prep**: By loading key tokens into the brain's short-term memory (context window) before watching a video, the learner reduces the "decoding noise," allowing more cognitive resources to be dedicated to content comprehension.
*   **Long-term Reinforcement**: While the prep is temporary, repeated exposure to the same tokens across different videos eventually makes the mnemonics redundant. This accumulation results in genuine lexical acquisition and improved overall comprehension.

## 7. Sustainability and Roadmap

VocabDeck is currently optimized for video preparation but lacks the infrastructure for long-term vocabulary management, such as **Cross-contextual Integration** (unified decks across different sources) and **SRS (Spaced Repetition Systems)**.

Maintaining a standalone learning application is resource-intensive. A more sustainable and realistic approach is integration with established ecosystems like **Anki**. By leveraging Anki's robust SRS and flexible data structures, the mnemonics and assets generated in VocabDeck can be managed and expanded over the long term, ensuring that the "beachheads" established during video prep are turned into permanent linguistic assets.
