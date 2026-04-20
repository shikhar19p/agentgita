# Gita GPT - Bhagavad Gita Grounded Agentic RAG System

A production-grade, research-quality Agentic RAG system that provides grounded, respectful, and deterministic responses based exclusively on the Bhagavad Gita.

## Core Principles

1. **Corpus is Authoritative** - No verse, translation, or Sanskrit text is ever invented
2. **LLMs for Interpretation Only** - Never for verse selection or generation
3. **Grounding is Non-Negotiable** - System refuses when grounding cannot be guaranteed
4. **Plurality is Preserved** - Multiple interpretations acknowledged where they exist
5. **Ambiguity is Explicit** - System never pretends the Gita answers what it doesn't

## System Architecture

### Multi-Node Agentic RAG Pipeline

```
Query → Intent Classification → Hybrid Retrieval → Contradiction Detection
  → Dialectical Reasoning → Grounding Verification → Plurality Check
  → Response Rendering OR Refusal
```

### Components

1. **Intent Classifier** - Determines domain, complexity, and refusal requirements
2. **Hybrid Retriever** - Dense (embeddings) + Sparse (BM25) + RRF fusion
3. **Contradiction Detector** - Identifies thematic tensions between verses
4. **Dialectical Reasoner** - Constructs perspectives and synthesis
5. **Grounding Verifier** - Validates every claim against verse text
6. **Plurality Checker** - Ensures balanced multi-perspective representation
7. **Response Renderer** - Formats final structured output
8. **Refusal Handler** - Generates respectful refusals with explanation

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# Clone or navigate to the project directory
cd gita_gpt

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key (for future LLM integration)
# OPENAI_API_KEY=your_key_here
```

## Usage

### Command Line Interface

**Single Query:**
```bash
python gita_gpt_cli.py "How do I deal with anger?"
```

**With Execution Trace:**
```bash
python gita_gpt_cli.py "What is the nature of the self?" --verbose
```

**Interactive Mode:**
```bash
python gita_gpt_cli.py --interactive
```

### Example Queries

- "How do I deal with anger?"
- "Should I focus on results or just do my work?"
- "What is the nature of the self?"
- "How can I control my wandering mind?"
- "Is it better to act or renounce action?"

### Out-of-Scope Queries (Will Be Refused)

- Financial advice
- Medical advice
- Cooking recipes
- Sports predictions
- Political opinions

## Response Format

Every successful response follows this structure:

```
User Query:
<your question>

Bhagavad Gita <chapter.verse>

Sanskrit (Transliteration):
<IAST transliteration>

English Translation:
<canonical translation>

Meaning of the Śloka:
<what the verse explicitly teaches>

Interpretation (Applied to the User's Question):
<grounded application to your query>

(Optional) Supportive Guidance:
<yogic practices if relevant>

(Optional) Visual Context:
<image prompts for visualization>
```

## Evaluation

Run the evaluation pipeline:

```bash
python evaluation/evaluator.py
```

Metrics tracked:
- **Retrieval Recall@K** - Relevant verses retrieved
- **Citation Precision** - Valid verse citations
- **Hallucination Rate** - Ungrounded claims
- **Refusal Accuracy** - Correct refusal decisions

## Configuration

Edit `config/config.yaml` to customize:

- Retrieval weights (dense vs sparse)
- Top-k results
- Context expansion settings
- Grounding strictness
- Logging level

## Project Structure

```
gita_gpt/
├── config/
│   └── config.yaml              # System configuration
├── data/
│   └── corpus.json              # Canonical verse corpus (31 verses)
├── src/
│   ├── core/
│   │   ├── state.py             # System state management
│   │   └── corpus_validator.py # Corpus loading and validation
│   ├── agents/
│   │   ├── intent_classifier.py
│   │   ├── contradiction_detector.py
│   │   ├── dialectical_reasoner.py
│   │   ├── grounding_verifier.py
│   │   └── plurality_checker.py
│   ├── retrieval/
│   │   ├── dense_retriever.py   # Sentence-BERT embeddings
│   │   ├── sparse_retriever.py  # BM25
│   │   └── hybrid_retriever.py  # RRF fusion
│   ├── rendering/
│   │   ├── response_renderer.py
│   │   └── refusal_handler.py
│   └── orchestrator/
│       └── orchestrator.py      # Main pipeline orchestration
├── evaluation/
│   ├── test_cases.json
│   ├── evaluator.py
│   └── failure_taxonomy.md
├── gita_gpt_cli.py              # CLI interface
├── requirements.txt
└── README.md
```

## Corpus Schema

Each verse entry contains:

```json
{
  "id": "BG_<chapter>_<verse(s)>",
  "chapter": <int>,
  "verses": [<int>, ...],
  "sloka_sanskrit_iast": "<IAST transliteration>",
  "translation_english": "<translation>",
  "themes": ["<theme>", ...],
  "keywords": ["<keyword>", ...],
  "context": {
    "chapter_theme": "<yoga type>",
    "speaker": "Krishna",
    "listener": "Arjuna",
    "setting": "<setting>"
  },
  "interpretive_notes": {
    "core_teaching": "<teaching>",
    "scope": "<scope>",
    "tone": "<tone>"
  },
  "supportive_practices": ["<practice>", ...],
  "image_tags": ["<tag>", ...]
}
```

## Known Limitations

1. **Corpus Size** - Currently 31 verses across 17 chapters (expandable)
2. **LLM Integration** - Interpretation section uses template-based reasoning (LLM integration planned)
3. **Image Generation** - Visual context tags present but not yet generating images
4. **Language Support** - English queries only (multilingual support planned)

## Future Extensions

1. **LLM-Enhanced Interpretation** - GPT-4 for nuanced interpretation generation
2. **Image Generation** - DALL-E/Stable Diffusion for visual context
3. **Expanded Corpus** - Full 700 verses with commentary integration
4. **Multi-Language** - Hindi, Sanskrit query support
5. **Conversation Memory** - Multi-turn dialogue with context retention
6. **Commentary Integration** - Shankaracharya, Ramanuja, modern commentaries

## Safety and Ethics

- **No Invention** - System never fabricates verses or teachings
- **Explicit Refusal** - Clear explanations when questions are out of scope
- **Grounding Verification** - Every claim validated against source text
- **Plurality Preservation** - Multiple valid interpretations acknowledged
- **Respectful Tone** - No preaching, no oversimplification

## License

This project is for educational and spiritual purposes. The Bhagavad Gita is a sacred text in the public domain.

## Contributing

Contributions welcome for:
- Corpus expansion (additional verses with proper schema)
- Evaluation test cases
- Failure mode identification
- Documentation improvements

## Citation

If you use this system in research, please cite:

```
Gita GPT: A Grounded Agentic RAG System for Bhagavad Gita Interpretation
[Your Name/Organization], 2026
```

---

**Om Shanti** 🙏
