# GITA GPT SYSTEM DOCUMENTATION

**Version:** 1.0.0  
**Date:** January 2026  
**Type:** Research-Grade Production System

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Design Philosophy](#2-design-philosophy)
3. [Corpus Schema](#3-corpus-schema)
4. [Agentic RAG Architecture](#4-agentic-rag-architecture)
5. [Node-by-Node Explanation](#5-node-by-node-explanation)
6. [Prompt Templates](#6-prompt-templates)
7. [Grounding & Verification Logic](#7-grounding--verification-logic)
8. [Failure Modes & Mitigations](#8-failure-modes--mitigations)
9. [Evaluation Methodology](#9-evaluation-methodology)
10. [Known Limitations](#10-known-limitations)
11. [Future Extensions](#11-future-extensions)

---

## 1. System Overview

### 1.1 Purpose

Gita GPT is a grounded, respectful, deterministic Bhagavad Gita-based assistant that:
- Interprets user queries automatically in a Gita context
- Retrieves relevant verses using hybrid search
- Constructs grounded interpretations with explicit citations
- Refuses gracefully when grounding cannot be guaranteed
- Preserves plurality of valid interpretations

### 1.2 Core Constraints

**ABSOLUTE CONSTRAINTS (Non-Negotiable):**

1. **Corpus Authority** - The Bhagavad Gita corpus is the only source of truth
2. **No Invention** - No verse, translation, or Sanskrit text may be invented
3. **LLM Scope** - LLMs used ONLY for interpretation, reasoning, phrasing
4. **LLM Prohibition** - LLMs NEVER used for verse selection, generation, or translation
5. **Grounding Requirement** - If grounding fails, system MUST refuse
6. **Ambiguity Acknowledgment** - System must explicitly acknowledge ambiguity
7. **No False Claims** - System never pretends Gita answers what it doesn't

**Violation of any constraint = System Failure**

### 1.3 System Behavior

**Input:** Natural language question (any domain)  
**Process:** 8-node agentic pipeline with stateful orchestration  
**Output:** Structured response OR respectful refusal

**Key Features:**
- Automatic Gita context interpretation (user doesn't say "according to Gita")
- Hybrid retrieval (dense embeddings + sparse BM25)
- Contradiction detection and dialectical reasoning
- Strict grounding verification
- Plurality enforcement
- Comprehensive execution tracing

---

## 2. Design Philosophy

### 2.1 Grounding Over Fluency

**Principle:** Accuracy and groundedness take absolute priority over response fluency.

**Implementation:**
- Template-based synthesis (not free-form LLM generation)
- Explicit verse citations for every claim
- Semantic alignment verification
- Fail-closed architecture (refuse when uncertain)

### 2.2 Plurality Over Singularity

**Principle:** Multiple valid interpretations must be preserved and presented.

**Implementation:**
- Contradiction detector identifies thematic tensions
- Dialectical reasoner constructs multiple perspectives
- Plurality checker ensures balanced representation
- No absolute language ("the only way", "must always")

### 2.3 Determinism Over Stochasticity

**Principle:** Core retrieval and reasoning must be deterministic and auditable.

**Implementation:**
- Verse selection via hybrid search (reproducible)
- Template-based reasoning (not LLM-generated)
- Full execution trace logging
- Stateful orchestration (inspectable at every step)

### 2.4 Refusal Over Overreach

**Principle:** Better to refuse than to misrepresent the Gita.

**Implementation:**
- Intent classification with refusal detection
- Out-of-scope pattern matching
- Grounding verification with strict mode
- Respectful refusal templates with explanations

---

## 3. Corpus Schema

### 3.1 Full Schema Definition

```json
{
  "id": "BG_<chapter>_<verse(s)>",
  "chapter": <integer>,
  "verses": [<integer>, ...],
  
  "sloka_sanskrit_iast": "<IAST transliteration>",
  "translation_english": "<canonical English translation>",
  
  "themes": ["<theme>", ...],
  "keywords": ["<Sanskrit keyword>", ...],
  
  "context": {
    "chapter_theme": "<yoga type>",
    "speaker": "Krishna",
    "listener": "Arjuna",
    "setting": "<setting description>"
  },
  
  "interpretive_notes": {
    "core_teaching": "<what the verse explicitly teaches>",
    "scope": "descriptive | ethical | metaphysical | devotional | philosophical | practical | cosmic",
    "tone": "analytical | instructional | reflective | clarifying | illustrative | ..."
  },
  
  "supportive_practices": ["<practice>", ...],
  "image_tags": ["<visual context tag>", ...]
}
```

### 3.2 Mandatory Fields

**Required in every entry:**
- `id` - Unique identifier (format: BG_chapter_verse)
- `chapter` - Chapter number (1-18)
- `verses` - List of verse numbers
- `sloka_sanskrit_iast` - IAST transliteration
- `translation_english` - English translation
- `themes` - List of thematic tags
- `keywords` - List of Sanskrit keywords

### 3.3 Optional Fields

**Enhance retrieval and interpretation:**
- `context` - Contextual metadata
- `interpretive_notes` - Core teaching, scope, tone
- `supportive_practices` - Grounded yogic practices
- `image_tags` - Visual context for future image generation

### 3.4 Validation Rules

**Enforced by CorpusValidator:**

1. All mandatory fields present
2. Field types correct (int, str, list, dict)
3. No duplicate verse IDs
4. Scope values from valid set
5. Verses list contains only integers
6. Themes and keywords are string lists

**Validation Modes:**
- **Strict Mode** - Warnings for unknown fields
- **Permissive Mode** - Unknown fields allowed

---

## 4. Agentic RAG Architecture

### 4.1 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER QUERY INPUT                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE 1: Intent Classification                              │
│  - Domain: ethical/theological/practical/metaphysical/OOS   │
│  - Complexity: simple/moderate/complex                      │
│  - Refusal requirement detection                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
              ┌──────┴──────┐
              │  Refuse?    │
              └──────┬──────┘
                 Yes │ No
      ┌──────────────┴──────────────┐
      │                              │
      ▼                              ▼
┌─────────────┐      ┌─────────────────────────────────────────┐
│  REFUSAL    │      │  NODE 2: Hybrid Retrieval               │
│  HANDLER    │      │  - Dense retrieval (embeddings)         │
└─────────────┘      │  - Sparse retrieval (BM25)              │
                     │  - Reciprocal Rank Fusion               │
                     │  - Context expansion (neighbors)        │
                     └────────────────┬────────────────────────┘
                                      │
                                      ▼
                     ┌─────────────────────────────────────────┐
                     │  NODE 3: Contradiction Detection        │
                     │  - Thematic tension identification      │
                     │  - Scope conflict detection             │
                     └────────────────┬────────────────────────┘
                                      │
                                      ▼
                     ┌─────────────────────────────────────────┐
                     │  NODE 4: Dialectical Reasoning          │
                     │  - Perspective construction             │
                     │  - Synthesis generation                 │
                     │  - Reasoning graph building             │
                     └────────────────┬────────────────────────┘
                                      │
                                      ▼
                     ┌─────────────────────────────────────────┐
                     │  NODE 5: Grounding Verification         │
                     │  - Claim extraction                     │
                     │  - Verse text alignment                 │
                     │  - Citation validation                  │
                     └────────────────┬────────────────────────┘
                                      │
                                      ▼
                               ┌──────┴──────┐
                               │  Grounded?  │
                               └──────┬──────┘
                                  Yes │ No
                       ┌──────────────┴──────────────┐
                       │                              │
                       ▼                              ▼
      ┌─────────────────────────────┐   ┌─────────────────┐
      │  NODE 6: Plurality Check    │   │  REFUSAL        │
      │  - Multi-perspective verify │   │  HANDLER        │
      │  - Scope diversity check    │   └─────────────────┘
      └────────────────┬────────────┘
                       │
                       ▼
      ┌─────────────────────────────────────────┐
      │  NODE 7: Response Rendering             │
      │  - Format verse reference               │
      │  - Extract meaning                      │
      │  - Construct interpretation             │
      │  - Add supportive guidance              │
      │  - Add visual context                   │
      └────────────────┬────────────────────────┘
                       │
                       ▼
      ┌─────────────────────────────────────────┐
      │         FINAL RESPONSE OUTPUT           │
      └─────────────────────────────────────────┘
```

### 4.2 Stateful Orchestration

**Central State Object (SystemState):**

```python
@dataclass
class SystemState:
    query: str
    intent: IntentMetadata
    retrieved_verses: List[RetrievedVerse]
    contradictions: List[Contradiction]
    reasoning_graph: List[ReasoningNode]
    grounding_results: List[GroundingResult]
    refusal_reason: Optional[RefusalReason]
    execution_trace: List[str]
    final_response: Optional[str]
```

**State Flow:**
1. Query → Intent metadata populated
2. Intent → Retrieved verses populated
3. Verses → Contradictions detected
4. Contradictions → Reasoning graph constructed
5. Reasoning → Grounding results validated
6. Grounding → Final response rendered OR refusal generated

**Traceability:**
- Every node adds to `execution_trace`
- Full state inspectable at any point
- No hidden state or side effects

---

## 5. Node-by-Node Explanation

### 5.1 Node 1: Intent Classification

**Purpose:** Determine query domain, complexity, and whether refusal is required.

**Input:** User query string  
**Output:** IntentMetadata (domain, complexity, requires_refusal, confidence)

**Algorithm:**

1. **Out-of-Scope Detection**
   - Pattern matching against OOS regex list
   - Domains: finance, medical, cooking, sports, politics, technology
   - If match → domain=OUT_OF_SCOPE, requires_refusal=True

2. **Domain Classification**
   - Keyword matching against domain dictionaries
   - Domains: ethical, theological, practical, metaphysical
   - Score each domain by keyword matches
   - Select highest-scoring domain

3. **Complexity Assessment**
   - Indicator phrase matching
   - Simple: "what is", "define", "meaning of"
   - Moderate: "how", "why", "explain"
   - Complex: "reconcile", "contradiction", "multiple perspectives"
   - Fallback: word count heuristic

4. **Confidence Calculation**
   - Based on keyword match count
   - 0 matches → 0.3
   - 1 match → 0.5
   - 2 matches → 0.7
   - 3+ matches → 0.9

**Example:**

Query: "How do I deal with anger?"
- OOS: No match
- Domain: practical (keywords: "how", "deal")
- Complexity: moderate (keyword: "how")
- Confidence: 0.7

### 5.2 Node 2: Hybrid Retrieval

**Purpose:** Retrieve relevant verses using dense + sparse fusion with context expansion.

**Input:** SystemState with query  
**Output:** SystemState with retrieved_verses populated

**Sub-Components:**

**A. Dense Retrieval (Sentence-BERT)**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Embedding dimension: 384
- Searchable text: translation + themes + keywords + core_teaching
- Similarity: Cosine similarity
- Top-k: Configurable (default: 10 for fusion input)

**B. Sparse Retrieval (BM25)**
- Algorithm: BM25Okapi
- Parameters: k1=1.5, b=0.75
- Tokenization: Lowercase, punctuation removal
- Searchable text: translation + themes + keywords
- Top-k: Configurable (default: 10 for fusion input)

**C. Reciprocal Rank Fusion (RRF)**

Formula:
```
score(verse) = dense_weight * (1 / (k + rank_dense)) 
             + sparse_weight * (1 / (k + rank_sparse))
```

Parameters:
- dense_weight: 0.6 (default)
- sparse_weight: 0.4 (default)
- k: 60 (RRF constant)

**D. Context Expansion**

For each top-k verse:
- Identify chapter and verse numbers
- Retrieve neighbor verses (±2 verses by default)
- Add neighbors with reduced score (0.5 * original)
- Prevents duplicate additions

**Output:**
- List of RetrievedVerse objects
- Each contains: verse_id, verse_data, relevance_score, retrieval_method
- Sorted by relevance score (descending)

### 5.3 Node 3: Contradiction Detection

**Purpose:** Identify thematic tensions and scope conflicts among retrieved verses.

**Input:** SystemState with retrieved_verses  
**Output:** SystemState with contradictions populated

**Detection Methods:**

**A. Thematic Tension Detection**

Predefined tension patterns:
```python
{
  "action_vs_renunciation": {
    "keywords": ["karma", "action", "sannyasa", "renunciation"],
    "themes": ["action", "detachment", "non_doership"]
  },
  "devotion_vs_knowledge": {
    "keywords": ["bhakti", "jnana"],
    "themes": ["devotion", "wisdom", "knowledge"]
  },
  "duty_vs_compassion": {
    "keywords": ["dharma", "duty", "ahimsa"],
    "themes": ["duty", "compassion", "non_violence"]
  },
  "self_effort_vs_divine_will": {
    "keywords": ["daiva", "karma", "effort", "surrender"],
    "themes": ["action", "surrender", "responsibility"]
  }
}
```

Algorithm:
1. For each tension pattern, group verses by keyword/theme matches
2. If ≥2 verses match a pattern → flag as contradiction
3. Severity: moderate (for thematic tensions)

**B. Scope Conflict Detection**

Algorithm:
1. Extract `interpretive_notes.scope` from each verse
2. If ≥3 different scopes present → flag as conflict
3. Severity: low (scope diversity is often valid)

**Output:**
- List of Contradiction objects
- Each contains: verse_ids, description, severity

### 5.4 Node 4: Dialectical Reasoning

**Purpose:** Construct reasoning graph with perspectives and synthesis.

**Input:** SystemState with retrieved_verses and contradictions  
**Output:** SystemState with reasoning_graph populated

**Modes:**

**A. Dialectical Mode (Contradictions Present)**

For each contradiction:
1. Extract Perspective A from first involved verse
2. Extract Perspective B from second involved verse
3. Generate synthesis using template matching

Synthesis Templates:
```python
{
  "action": "Both perspectives address different aspects of action: 
             one emphasizes engagement, the other detachment. 
             They are complementary rather than contradictory.",
  
  "devotion": "These verses present different paths (jnana and bhakti) 
               which the Gita treats as complementary approaches.",
  
  "duty": "The tension between duty and compassion is resolved 
           through understanding one's svadharma in context.",
  
  "effort": "Divine will and self-effort are not opposed; 
             effort is the means through which divine will manifests."
}
```

**B. Unified Mode (No Contradictions)**

1. Extract primary teaching from highest-ranked verse
2. Extract supporting teachings from next 2 verses
3. Create reasoning nodes for primary + support

**Reasoning Node Structure:**
```python
@dataclass
class ReasoningNode:
    claim: str
    supporting_verses: List[str]
    grounded: bool
    confidence: float
```

**Output:**
- List of ReasoningNode objects
- Each claim explicitly tied to verse IDs
- Confidence scores assigned

### 5.5 Node 5: Grounding Verification

**Purpose:** Validate that every claim in reasoning graph is grounded in verse text.

**Input:** SystemState with reasoning_graph and retrieved_verses  
**Output:** SystemState with grounding_results populated, refusal_reason set if failed

**Algorithm:**

For each ReasoningNode:

1. **Citation Check**
   - Verify supporting_verses list is non-empty
   - If empty → is_grounded = False

2. **Verse Retrieval**
   - Lookup each cited verse_id in retrieved_verses
   - If not found → is_grounded = False

3. **Semantic Alignment Check**
   - Extract verse translation text
   - Tokenize claim and verse text
   - Calculate word overlap ratio
   - Threshold: 30% overlap required
   - Special case: Template phrases auto-pass
     - "Perspective A:", "Perspective B:", "Synthesis:", etc.

4. **Grounding Decision**
   - If all checks pass → is_grounded = True
   - Otherwise → is_grounded = False
   - Update ReasoningNode.grounded field

**Strict Mode:**
- If ANY claim is ungrounded → set refusal_reason = INSUFFICIENT_GROUNDING
- System will refuse to generate response

**Permissive Mode:**
- Allow some ungrounded claims
- Mark them clearly in output

**Output:**
- List of GroundingResult objects
- Each contains: claim, is_grounded, supporting_verse_ids, explanation
- refusal_reason set if strict mode failure

### 5.6 Node 6: Plurality Check

**Purpose:** Ensure multiple perspectives are preserved and no single interpretation is asserted as absolute.

**Input:** SystemState with reasoning_graph and retrieved_verses  
**Output:** SystemState (trace updated, no structural changes)

**Checks:**

**A. Multiple Perspectives Detection**
- Count reasoning nodes with "Perspective A/B" labels
- If ≥2 → flag as multi-perspective response
- Trace: "Multiple perspectives detected"

**B. Scope Diversity Detection**
- Extract unique scopes from retrieved verses
- If ≥2 scopes → flag for balanced treatment
- Trace: "Multiple interpretive scopes present"

**C. Absolute Language Detection** (Future)
- Scan claims for absolute phrases:
  - "the only way", "must always", "never", "the correct interpretation"
- If found → flag for revision
- Currently: detection only, no enforcement

**Output:**
- Execution trace entries
- No refusal (informational only)

### 5.7 Node 7: Response Rendering

**Purpose:** Format final structured response according to specification.

**Input:** SystemState with all fields populated  
**Output:** SystemState with final_response string

**Response Structure:**

```
User Query:
<query>

Bhagavad Gita <chapter.verse(s)> (English Translation)

Sanskrit (Transliteration):
<sloka_sanskrit_iast>

English Translation:
<translation_english>

Meaning of the Śloka:
<core_teaching OR translation_english>

Interpretation (Applied to the User's Question):
<constructed from reasoning_graph>

(Optional) Supportive Guidance:
<supportive_practices, max 3>

(Optional) Visual Context:
<image_tags, max 2>
```

**Rendering Logic:**

1. **Primary Verse Selection**
   - Use highest-ranked retrieved verse

2. **Verse Reference Formatting**
   - Single verse: "2.47"
   - Multiple verses: "2.62-63"

3. **Meaning Extraction**
   - Prefer `interpretive_notes.core_teaching`
   - Fallback: `translation_english`

4. **Interpretation Construction**
   - Extract claims from reasoning_graph where grounded=True
   - Remove template prefixes ("Primary teaching:", etc.)
   - Join with double newlines
   - Fallback: "[Interpretation requires LLM integration - placeholder]"

5. **Supportive Guidance**
   - Extract `supportive_practices` from primary verse
   - Limit to 3 practices
   - Format as comma-separated list

6. **Visual Context**
   - Extract `image_tags` from primary verse
   - Limit to 2 tags
   - Format as numbered list

**Output:**
- Complete formatted response string
- Stored in state.final_response

### 5.8 Node 8: Refusal Handler

**Purpose:** Generate respectful refusal with explanation when system cannot provide grounded response.

**Input:** SystemState with refusal_reason set  
**Output:** SystemState with final_response (refusal message)

**Refusal Templates:**

**A. OUT_OF_SCOPE**
```
Title: Question Outside Bhagavad Gita Scope
Explanation: The Bhagavad Gita primarily addresses questions of dharma, 
             self-knowledge, devotion, and the nature of reality. 
             Your question appears to be outside this scope.
Suggestion: If you have a question about ethics, purpose, inner conflict, 
            or spiritual understanding, please feel free to ask.
```

**B. INSUFFICIENT_GROUNDING**
```
Title: Insufficient Grounding in Verses
Explanation: While the Gita may touch upon themes related to your question, 
             I cannot construct a response that is fully grounded in specific 
             verses without risk of overreach or misrepresentation.
Suggestion: You might try rephrasing your question more specifically, or 
            asking about a particular aspect that the Gita directly addresses.
```

**C. CONTRADICTORY_EVIDENCE**
```
Title: Multiple Contradictory Perspectives
Explanation: The verses relevant to your question present perspectives that 
             appear contradictory without sufficient context for synthesis.
Suggestion: Consider asking about specific verses or concepts, or how 
            different paths relate to your question.
```

**D. AMBIGUOUS_INTENT**
```
Title: Ambiguous Question
Explanation: Your question could be interpreted in multiple ways, and I want 
             to ensure I provide a response grounded in the appropriate verses.
Suggestion: Please clarify your question or provide more context.
```

**Format:**
```
User Query:
<query>

================================================================================

**<Title>**

<Explanation>

<Suggestion>

================================================================================

Note: The Bhagavad Gita is a sacred text addressing eternal questions of
dharma, self-realization, and devotion. I aim to provide responses that
are faithful to the text and grounded in specific verses.
```

---

## 6. Prompt Templates

### 6.1 Current Implementation

**Note:** Current system uses template-based reasoning, NOT LLM prompts.

**Synthesis Templates** (Dialectical Reasoner):
- Action vs Renunciation
- Devotion vs Knowledge
- Duty vs Compassion
- Self-Effort vs Divine Will

**Refusal Templates** (Refusal Handler):
- Out of Scope
- Insufficient Grounding
- Contradictory Evidence
- Ambiguous Intent

### 6.2 Future LLM Integration

**Planned Prompts for Interpretation Generation:**

**System Prompt:**
```
You are an interpreter for the Bhagavad Gita. Your role is to apply 
the teachings of specific verses to user questions.

CRITICAL RULES:
1. Use ONLY the provided verse text
2. Do NOT invent or paraphrase verses
3. Do NOT make claims beyond what the verse explicitly states
4. Acknowledge ambiguity where it exists
5. Preserve plurality of valid interpretations
6. Cite verse IDs for every claim

Your interpretation must be:
- Grounded in the verse text
- Respectful and non-preachy
- Contextually applied to the user's question
- Free from modern psychology unless aligned with the text
```

**User Prompt Template:**
```
User Question: {query}

Verse {verse_id}:
Sanskrit: {sloka_sanskrit_iast}
Translation: {translation_english}
Core Teaching: {core_teaching}

Additional Context:
{supporting_verses_if_any}

Task: Provide a grounded interpretation of how this verse applies to 
the user's question. Stay strictly within the bounds of what the verse 
explicitly teaches.
```

---

## 7. Grounding & Verification Logic

### 7.1 Grounding Definition

**A claim is grounded if and only if:**

1. It cites at least one verse ID
2. The cited verse(s) are in the retrieved set
3. The claim's semantic content aligns with the verse text
4. No part of the claim contradicts the verse

### 7.2 Semantic Alignment Algorithm

**Current Implementation:**

```python
def _check_semantic_alignment(claim: str, verse_texts: List[str]) -> bool:
    # Special case: Template phrases auto-pass
    if any(phrase in claim.lower() for phrase in [
        "perspective a:", "perspective b:", "synthesis:", 
        "primary teaching:", "supporting context:"
    ]):
        return True
    
    # Tokenize claim and verses
    claim_words = set(re.findall(r'\b\w+\b', claim.lower()))
    verse_words = set(re.findall(r'\b\w+\b', " ".join(verse_texts).lower()))
    
    # Calculate overlap
    common_words = claim_words.intersection(verse_words)
    overlap_ratio = len(common_words) / len(claim_words)
    
    # Threshold: 30% overlap required
    return overlap_ratio > 0.3
```

**Limitations:**
- Simple word overlap (not semantic similarity)
- Fixed 30% threshold (not adaptive)
- No handling of synonyms or paraphrasing

**Future Enhancements:**
- Sentence-BERT similarity scoring
- Adaptive thresholds based on claim type
- Entailment checking (NLI models)
- Manual review for edge cases

### 7.3 Strict vs Permissive Modes

**Strict Mode (Default):**
- ALL claims must be grounded
- Single ungrounded claim → system refuses
- Used in production for safety

**Permissive Mode:**
- Some ungrounded claims allowed
- Marked clearly in output
- Used for development/testing

**Configuration:**
```yaml
reasoning:
  grounding:
    strict_mode: true
    fail_on_unsupported_claims: true
```

### 7.4 Citation Validation

**Requirements:**

1. **Explicit Citation**
   - Every ReasoningNode must have non-empty supporting_verses list

2. **Verse Availability**
   - All cited verse_ids must be in retrieved_verses

3. **No Circular Citations**
   - Claim cannot cite itself

4. **No Phantom Citations**
   - Cannot cite verses not in corpus

**Validation Process:**
```python
for node in reasoning_graph:
    if not node.supporting_verses:
        node.grounded = False
        continue
    
    for verse_id in node.supporting_verses:
        if verse_id not in [rv.verse_id for rv in retrieved_verses]:
            node.grounded = False
            break
```

---

## 8. Failure Modes & Mitigations

### 8.1 Retrieval Failures

**Low Recall:**
- **Symptom:** Relevant verses not in top-k
- **Causes:** Semantic mismatch, weak keyword coverage
- **Mitigation:** Tune weights, expand corpus keywords, increase k

**Low Precision:**
- **Symptom:** Irrelevant verses retrieved
- **Causes:** Over-broad query, weak theme matching
- **Mitigation:** Stricter thresholds, improve intent classification

### 8.2 Grounding Failures

**Unsupported Claims:**
- **Symptom:** Reasoning nodes not grounded in verses
- **Causes:** Synthesis beyond verse content, weak alignment
- **Mitigation:** Template-only synthesis, stricter verification

**Citation Errors:**
- **Symptom:** Claims cite non-supporting verses
- **Causes:** Verse ID mismatches, weak thresholds
- **Mitigation:** Explicit text matching, manual review

### 8.3 Refusal Failures

**False Refusals:**
- **Symptom:** System refuses answerable questions
- **Causes:** Over-sensitive OOS detection, strict grounding
- **Mitigation:** Tune thresholds, permissive mode option

**Missed Refusals:**
- **Symptom:** System answers out-of-scope questions
- **Causes:** Incomplete OOS patterns, weak classification
- **Mitigation:** Expand pattern list, confidence thresholds

### 8.4 Contradiction Handling Failures

**Missed Contradictions:**
- **Symptom:** Verse tensions not detected
- **Causes:** Limited tension indicators, scope conflicts missed
- **Mitigation:** Expand indicator dictionary, yoga-path detection

**False Contradictions:**
- **Symptom:** Complementary verses flagged as contradictory
- **Causes:** Over-sensitive keyword matching
- **Mitigation:** Complementarity patterns, context-aware detection

### 8.5 Plurality Failures

**Single Interpretation Assertion:**
- **Symptom:** One interpretation presented as definitive
- **Causes:** Absolute language in templates, weak enforcement
- **Mitigation:** Rewrite templates with hedging, strengthen checks

**Ambiguity Avoidance:**
- **Symptom:** Legitimate ambiguity not acknowledged
- **Causes:** Forced synthesis, oversimplification
- **Mitigation:** "Ambiguity acknowledged" response type

### 8.6 System-Level Failures

**Corpus Coverage Gaps:**
- **Symptom:** Relevant verses not in corpus
- **Causes:** Limited corpus size (31 verses)
- **Mitigation:** Systematic corpus expansion

**Performance Degradation:**
- **Symptom:** Slow response times
- **Causes:** Embedding inference, multiple retrieval passes
- **Mitigation:** Cache embeddings, optimize fusion

**Adversarial Attacks:**
- **Symptom:** Prompt injection, hallucination induction
- **Causes:** No input sanitization, weak grounding
- **Mitigation:** Input validation, strict mode, template-only synthesis

**Full Taxonomy:** See `evaluation/failure_taxonomy.md`

---

## 9. Evaluation Methodology

### 9.1 Metrics

**A. Retrieval Recall@K**

Definition: Proportion of expected verses retrieved in top-k results

Formula:
```
Recall@K = |Expected ∩ Retrieved_Top_K| / |Expected|
```

**B. Citation Precision**

Definition: Proportion of cited verses that are valid (in retrieved set)

Formula:
```
Precision = |Valid_Citations| / |All_Citations|
```

**C. Hallucination Rate**

Definition: Proportion of reasoning nodes that are ungrounded

Formula:
```
Hallucination_Rate = Ungrounded_Claims / Total_Claims
```

**D. Refusal Accuracy**

Definition: Proportion of correct refusal decisions

Formula:
```
Refusal_Accuracy = Correct_Refusals / (Correct_Refusals + Incorrect_Refusals)
```

### 9.2 Test Cases

**Structure:**
```json
{
  "id": "test_001",
  "query": "<question>",
  "expected_verses": ["BG_x_y", ...],
  "expected_domain": "practical|ethical|theological|metaphysical|out_of_scope",
  "should_refuse": true|false,
  "notes": "<description>"
}
```

**Categories:**
- In-scope practical questions
- In-scope metaphysical questions
- Out-of-scope questions (financial, medical, etc.)
- Contradiction-inducing questions
- Ambiguous questions

**Current Test Suite:** 10 test cases (see `evaluation/test_cases.json`)

### 9.3 Evaluation Process

**Automated Evaluation:**

```bash
python evaluation/evaluator.py
```

**Steps:**
1. Load test cases
2. For each test case:
   - Run intent classification
   - Check refusal accuracy
   - Run retrieval (if not refused)
   - Calculate recall@k
   - Run reasoning pipeline
   - Calculate citation precision
   - Calculate hallucination rate
3. Aggregate metrics
4. Generate report
5. Save results to JSON

**Manual Review:**
- Response quality assessment
- Grounding verification
- Plurality preservation check
- Tone and respectfulness evaluation

### 9.4 Benchmarking

**Baseline Targets:**
- Retrieval Recall@5: ≥ 0.70
- Citation Precision: ≥ 0.90
- Hallucination Rate: ≤ 0.10
- Refusal Accuracy: ≥ 0.85

**Current Performance:** (Run evaluation to populate)

---

## 10. Known Limitations

### 10.1 Corpus Limitations

**Size:**
- Current: 31 verses across 17 chapters
- Full Gita: 700 verses across 18 chapters
- Coverage: ~4.4%

**Impact:**
- Many queries cannot be answered
- Limited thematic diversity
- Uneven chapter representation

**Mitigation:**
- Systematic corpus expansion planned
- Prioritize high-frequency themes
- Ensure representative sampling

### 10.2 Interpretation Limitations

**Template-Based Reasoning:**
- Current: Fixed synthesis templates
- Limitation: Not adaptive to query nuances
- Impact: Generic interpretations

**No LLM Integration:**
- Interpretation section uses templates or placeholders
- Cannot generate nuanced, query-specific interpretations
- Limits response quality

**Mitigation:**
- LLM integration planned (GPT-4)
- Strict prompting with grounding constraints
- Verification layer post-LLM generation

### 10.3 Retrieval Limitations

**Semantic Mismatch:**
- Embedding model may not capture Gita-specific semantics
- Modern language vs classical concepts
- Impact: Relevant verses missed

**Context Expansion:**
- Simple neighbor retrieval (±2 verses)
- Doesn't consider chapter boundaries
- May retrieve unrelated verses

**Mitigation:**
- Fine-tune embeddings on Gita corpus
- Smarter context expansion (chapter-aware)
- Hybrid approach with keyword boosting

### 10.4 Grounding Limitations

**Simple Word Overlap:**
- Current alignment check is basic
- Doesn't handle paraphrasing or synonyms
- 30% threshold is arbitrary

**No Entailment Checking:**
- Cannot verify logical entailment
- Weak detection of contradictions
- Impact: Some ungrounded claims may pass

**Mitigation:**
- Sentence-BERT similarity scoring
- NLI models for entailment
- Manual review for critical claims

### 10.5 Language Limitations

**English Only:**
- Queries must be in English
- No Hindi, Sanskrit, or other language support
- Limits accessibility

**Mitigation:**
- Multilingual query support planned
- Translation layer for non-English queries
- Maintain English corpus as source of truth

### 10.6 Image Generation

**Not Implemented:**
- Visual context tags present but unused
- No image generation capability
- Impact: Incomplete response format

**Mitigation:**
- DALL-E/Stable Diffusion integration planned
- Grounded prompts from image_tags
- Iconography validation

---

## 11. Future Extensions

### 11.1 LLM-Enhanced Interpretation

**Goal:** Generate nuanced, query-specific interpretations while maintaining grounding.

**Approach:**
1. Use GPT-4 with strict system prompt
2. Provide verse text and query as context
3. Generate interpretation
4. Verify grounding post-generation
5. Reject if ungrounded

**Safeguards:**
- Temperature: 0.3 (low randomness)
- Max tokens: 1500
- Explicit citation requirements in prompt
- Post-generation verification layer

### 11.2 Image Generation

**Goal:** Generate visual context images grounded in Gita iconography.

**Approach:**
1. Extract image_tags from selected verse
2. Construct grounded prompt
3. Generate image via DALL-E/Stable Diffusion
4. Validate against iconographic standards
5. Include in response

**Example Prompt:**
```
Generate a traditional Indian miniature painting style image depicting:
Krishna teaching Arjuna on the battlefield of Kurukshetra.
Style: Classical Indian art, respectful, spiritual.
No modern elements.
```

### 11.3 Expanded Corpus

**Goal:** Cover all 700 verses of the Bhagavad Gita.

**Approach:**
1. Systematic verse selection (chapter by chapter)
2. Ensure representative theme coverage
3. Add interpretive_notes for each verse
4. Validate translations against multiple sources
5. Incremental indexing and testing

**Priority Chapters:**
- Chapter 2 (Sankhya Yoga) - foundational
- Chapter 3 (Karma Yoga) - action
- Chapter 6 (Dhyana Yoga) - meditation
- Chapter 12 (Bhakti Yoga) - devotion
- Chapter 18 (Moksha Sannyasa Yoga) - synthesis

### 11.4 Commentary Integration

**Goal:** Incorporate traditional commentaries (Shankaracharya, Ramanuja, etc.)

**Approach:**
1. Add commentary field to corpus schema
2. Link commentaries to specific verses
3. Use in dialectical reasoning for multiple perspectives
4. Cite commentary source explicitly

**Schema Extension:**
```json
{
  "commentaries": [
    {
      "author": "Shankaracharya",
      "tradition": "Advaita Vedanta",
      "text": "<commentary excerpt>",
      "emphasis": "<key point>"
    }
  ]
}
```

### 11.5 Multi-Language Support

**Goal:** Support queries in Hindi, Sanskrit, and other languages.

**Approach:**
1. Add translation layer (Google Translate API)
2. Translate query to English
3. Process through existing pipeline
4. Translate response back to source language
5. Maintain English corpus as source of truth

**Challenges:**
- Semantic loss in translation
- Sanskrit technical terms
- Cultural context preservation

### 11.6 Conversation Memory

**Goal:** Support multi-turn dialogue with context retention.

**Approach:**
1. Maintain conversation state across turns
2. Reference previous verses and interpretations
3. Build cumulative understanding
4. Clear conversation history on topic shift

**Schema:**
```python
@dataclass
class ConversationState:
    turns: List[SystemState]
    cumulative_verses: Set[str]
    topic_thread: str
    last_updated: datetime
```

### 11.7 Advanced Contradiction Resolution

**Goal:** Handle complex contradictions with multi-level synthesis.

**Approach:**
1. Detect contradiction types (apparent vs real)
2. Apply context-specific resolution strategies
3. Consult commentaries for traditional resolutions
4. Present multiple valid resolutions

**Contradiction Types:**
- Apparent (resolved by context)
- Dialectical (resolved by synthesis)
- Perspectival (multiple valid views)
- Irresolvable (acknowledge ambiguity)

### 11.8 Personalization

**Goal:** Adapt responses to user's spiritual path and background.

**Approach:**
1. Optional user profile (karma/bhakti/jnana orientation)
2. Emphasize relevant verses for user's path
3. Adjust tone and complexity
4. Maintain grounding and plurality

**Privacy:**
- Opt-in only
- No tracking without consent
- Local storage of preferences

---

## Appendices

### A. Configuration Reference

See `config/config.yaml` for full configuration options.

### B. API Reference

See code documentation in `src/` modules.

### C. Corpus Expansion Guidelines

1. Select verses systematically (chapter order)
2. Ensure IAST transliteration accuracy
3. Use authoritative English translations
4. Add themes and keywords comprehensively
5. Include interpretive_notes where possible
6. Validate schema compliance
7. Test retrieval before committing

### D. Contribution Guidelines

1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Ensure evaluation metrics don't degrade
5. Update documentation
6. Submit pull request

### E. Deployment Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Validate corpus (`python test_corpus.py`)
- [ ] Run evaluation (`python evaluation/evaluator.py`)
- [ ] Check metrics against baselines
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Test refusal cases
- [ ] Test adversarial inputs
- [ ] Review execution traces
- [ ] Deploy with graceful degradation

---

**End of Documentation**

**Version:** 1.0.0  
**Last Updated:** January 2026  
**Maintainer:** Gita GPT Development Team

**Om Shanti** 🙏
