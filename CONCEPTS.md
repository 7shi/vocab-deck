# Design Concepts of VocabDeck (CONCEPTS)

## 1. Objective: Curiosity-Driven Authentic Learning
VocabDeck is not just a language learning tool; its primary goal is to enable **direct access to the history and geography of a region through its native language.**

*   **Anti-Artificial Skits**: We reject the "trivial dialogues" found in traditional textbooks (e.g., ordering coffee). Instead, we dive straight into "authentic content"—YouTube documentaries, historical narrations, and primary source articles.
*   **Language for Knowledge**: Language is treated as a tool, not an end in itself. Intellectual curiosity about a region's history or culture serves as the primary engine (fuel) for sustained learning.
*   **Focus on Receptive Skills (Input)**: Acknowledging that opportunities for active speaking are often limited, we concentrate resources on maximizing the quality and volume of "reception"—listening to narrations and grasping context.

## 2. The 3-Layer Priority Model
To optimize cognitive load and transition efficiently to "real-world" content (e.g., watching a video), vocabulary is categorized into three layers:

*   **Layer 1: High-Frequency & High Semantic Density (~10 words)**
    *   The structural backbone of the language. These act as "core tokens" (in LLM terms), serving as a compass for navigating the logical flow of sentences.
*   **Layer 2: Domain-Specific Vocabulary (~10 words)**
    *   Keywords essential for understanding the specific topic (History, Geography, etc.). These determine the resolution of the context.
*   **Layer 3: Proper Nouns (Unlimited)**
    *   Names of people, places, and events—the anchors to **Local Reality**.
    *   By recognizing these in their "local sound" rather than through a translation filter, we achieve a more authentic understanding. Since the goal is "Sound Identification (ID)," there is no limit on the number of entries.

## 3. Cognitive Pipeline: Shortcuts to Meaning
To bridge the gap between "unknown sounds" and "concepts," we employ a three-step approach inspired by cognitive science and LLM metaphors.

### Step 1: Sound Fixing (Tokenization) [Hint]
We map the unknown sounds of a foreign language onto familiar sound patterns of a known language (e.g., Japanese).
*   **Role**: Acting as a "Tokenizer," this allows the brain to register unknown noise as a "known token," creating a foundation for processing.
*   **State**: Establishing the feeling of "I don't know the meaning yet, but I recognize this sound."

### Step 2: Provisional Bridging (Adapter) [Memo]
We temporarily connect the "fixed sound" to a "meaning" through narratives or phonetic mnemonics (*Kojitsuke*).
*   **Role**: Acting as an "Adapter" (like LoRA/PEFT), this adds a temporary edge to the brain's existing knowledge graph.
*   **State**: Securing a "mnemonic hook" to prevent the sound from slipping away.

### Step 3: Authentic Meaning (Contextual Training) [Example/Original Content]
Through various usage examples and the original content itself (the video/article), we solidify the "relative position" and "semantic distribution" of the word.
*   **Role**: Gradually removing the "provisional bridge" and transitioning to a state of "true understanding"—where the sound connects directly to the concept without mental translation.

## 4. Operational Philosophy: Low-Friction Warm-Up
This system is designed as a **"5-10 minute warm-up"** before engaging with the main content.

*   **Brain Priming**: By loading key tokens into the brain's "cache" (short-term memory) beforehand, we ensure that during the actual video/article, the brain isn't exhausted by "decoding noise" and can dedicate all its resources to "comprehending content."
*   **Sustainability**: To ensure consistency, we strictly limit Layer 1 and 2 vocabulary to about 10 words each, keeping the cognitive load manageable.

## 5. Future Vision: Personal Dynamic Lexicon
While the current system maintains independence for each source (TOML), the long-term goal is to integrate accumulated mnemonics (Memos) and usage data (Examples) into a user's unique, multi-dimensional "map of concepts"—a personal dynamic lexicon.
