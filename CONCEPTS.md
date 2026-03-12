# Design Concepts of VocabDeck (CONCEPTS)

## 1. Objective: Curiosity-Driven Efficiency in Language Learning
VocabDeck is a vocabulary study support system designed with the assumption that existing video content, such as YouTube, will be used as learning material. Its design incorporates several intentions to efficiently "familiarize the brain" with an unknown language.

*   **Language for Knowledge**: The primary goal is not necessarily the mastery of the language itself, but rather **direct access to the "native history and geography"** narrated through that language.
*   **Curiosity as Fuel**: Instead of memorizing textbook-style fixed phrases, the motivation for learning is to understand topics of personal interest, such as historical episodes or geographical facts.
*   **Focus on Receptive Skills (Input)**: Considering that opportunities for active conversation are often limited, we focus on enhancing "receptive skills"—listening to narrations and understanding context. Language is positioned as a tool for accessing the knowledge (content) of the region.

## 2. The 3-Layer Priority Model: Cognitive Load Management
To distribute the learning burden and facilitate a smooth transition to video viewing, vocabulary is categorized into three layers based on its nature:

*   **Layer 1: High-Frequency & High Semantic Density (~10 words)**
    *   The structural backbone of the language. Like "core tokens" in an LLM, these serve as a compass for grasping the logical structure and following the thread of the story.
*   **Layer 2: Domain-Specific Vocabulary (~10 words)**
    *   Terms specialized for specific themes like history or geography. These are keys to understanding the topic-specific context.
*   **Layer 3: Proper Nouns (Unlimited)**
    *   Names of people, places, and events—the anchors to **Local Reality**.
    *   By recognizing these in their "local sound" rather than through a translation filter, auditory comprehension during video viewing is significantly improved.

## 3. Cognitive Pipeline: Fixing Sounds and Bridging Meaning
The process of transforming unknown sounds into "meaningful words" assumes a three-step approach to assist brain processing.

### Step 1: Sound Fixing (Tokenization) [Hint]
We map the unknown sounds of a foreign language onto familiar sound patterns of a known language (e.g., Japanese).
*   **Role**: Enables the brain to identify unknown noise as "known tokens," creating a foundation for listening.
*   **State**: Establishing the feeling of "I don't know the meaning yet, but I recognize this sound as a chunk (I can repeat it)."

### Step 2: Provisional Bridging (Adapter) [Memo]
We temporarily connect the "fixed sound" to a "meaning" through narratives or phonetic mnemonics (*Kojitsuke*).
*   **Role**: Utilizing existing memories (Japanese vocabulary or episodic memory) to "attach" a temporary meaning to the unknown sound, acting as an "Adapter" (like LoRA).
*   **State**: Securing a "mnemonic hook" to assist recall during video viewing until the memory is solidified.

### Step 3: Authentic Meaning (Acquisition through Practice) [Examples/Original Content]
Finally, through repeated exposure to various contexts, such as the video itself or usage examples, the original meaning and nuances of the word are solidified in the brain.
*   **Role**: Gradually making the "provisional bridge" unnecessary and connecting the sound directly to the concept.

## 4. Operational Philosophy: "Context Engineering" for Videos
The "warm-up" in VocabDeck functions as a **5-10 minute pre-processing step** before engaging with the main content.

*   **Context Engineering for Inference**: If watching a video is seen as "Inference," this process is not "Learning" (model update), but rather **"Context Engineering"** (controlling the context during inference).
*   **Brain Preparation**: By familiarizing the "sounds" of key words beforehand and placing them in the brain's short-term memory (context window), we ensure that during the actual video, the brain isn't exhausted by "decoding noise" and can focus entirely on "comprehending content."
*   **Low-Friction Design**: To ensure consistency, we strictly limit Layer 1 and 2 vocabulary to about 10 words each, keeping the cognitive load manageable to make it a sustainable routine.

## 5. Future Vision: Sustainability and Versatility
While the current system uses the browser's Web Speech API to achieve high-quality TTS for minor languages at zero cost, long-term maintainability and the convenience of integration with existing platforms are important considerations.

*   **Integration with Existing Infrastructure**: Integrating with established learning platforms like Anki can provide a more efficient environment for long-term review (learning).
*   **Cloud TTS for Audio Export**: We are considering supporting the export of audio files via cloud services (e.g., Google Cloud TTS) to facilitate the creation of Anki decks.
*   **Personal Dynamic Lexicon**: Integrating user-created mnemonics (Memos) into a cross-source database to build a unique, multi-dimensional "map of concepts."
