# Gita GPT Failure Taxonomy

## 1. RETRIEVAL FAILURES

### 1.1 Low Recall
**Description**: Relevant verses not retrieved in top-k results  
**Causes**:
- Semantic mismatch between query and verse embeddings
- Sparse retrieval missing key terms
- Context expansion not capturing neighboring verses

**Mitigation**:
- Tune hybrid retrieval weights
- Expand keyword coverage in corpus
- Increase top-k parameter
- Add query expansion/reformulation

### 1.2 Low Precision
**Description**: Irrelevant verses retrieved  
**Causes**:
- Over-broad query interpretation
- Weak theme/keyword matching
- Context expansion retrieving unrelated verses

**Mitigation**:
- Stricter relevance thresholding
- Improve intent classification
- Reduce context expansion radius

## 2. GROUNDING FAILURES

### 2.1 Unsupported Claims
**Description**: Reasoning nodes not grounded in retrieved verses  
**Causes**:
- Dialectical reasoner generating synthesis beyond verse content
- Weak semantic alignment checking
- Overgeneralization from specific verses

**Mitigation**:
- Stricter grounding verification
- Template-based synthesis (not free-form)
- Explicit citation requirements

### 2.2 Citation Errors
**Description**: Claims cite verses that don't support them  
**Causes**:
- Reasoning node construction errors
- Verse ID mismatches
- Weak semantic alignment thresholds

**Mitigation**:
- Improve semantic alignment algorithm
- Add explicit verse text matching
- Manual review of reasoning templates

## 3. REFUSAL FAILURES

### 3.1 False Refusals
**Description**: System refuses answerable questions  
**Causes**:
- Over-sensitive out-of-scope detection
- Overly strict grounding requirements
- Intent misclassification

**Mitigation**:
- Tune intent classifier thresholds
- Relax grounding in non-strict mode
- Add query clarification prompts

### 3.2 Missed Refusals
**Description**: System attempts to answer out-of-scope questions  
**Causes**:
- Incomplete out-of-scope patterns
- Weak domain classification
- Retrieval returning spurious matches

**Mitigation**:
- Expand out-of-scope pattern list
- Add domain-specific refusal logic
- Implement confidence thresholds

## 4. CONTRADICTION HANDLING FAILURES

### 4.1 Missed Contradictions
**Description**: System doesn't detect verse tensions  
**Causes**:
- Limited tension indicator coverage
- Verses from different yogas not flagged
- Scope conflicts not detected

**Mitigation**:
- Expand tension indicator dictionary
- Add yoga-path conflict detection
- Improve scope diversity checking

### 4.2 False Contradictions
**Description**: System flags non-contradictory verses  
**Causes**:
- Over-sensitive keyword matching
- Complementary perspectives treated as contradictory
- Scope diversity misinterpreted

**Mitigation**:
- Refine tension detection logic
- Add complementarity patterns
- Context-aware contradiction detection

## 5. PLURALITY FAILURES

### 5.1 Single Interpretation Assertion
**Description**: System presents one interpretation as definitive  
**Causes**:
- Synthesis templates too absolute
- Plurality checker not enforcing balance
- Response rendering favoring primary verse

**Mitigation**:
- Rewrite synthesis templates with hedging
- Strengthen plurality enforcement
- Ensure multi-perspective representation

### 5.2 Ambiguity Avoidance
**Description**: System doesn't acknowledge legitimate ambiguity  
**Causes**:
- Forced synthesis when none exists
- Dialectical reasoner oversimplifying
- Refusal logic not triggered for ambiguous cases

**Mitigation**:
- Add "ambiguity acknowledged" response type
- Allow dialectical presentation without synthesis
- Refusal for irresolvable contradictions

## 6. RESPONSE RENDERING FAILURES

### 6.1 Format Violations
**Description**: Output doesn't match required structure  
**Causes**:
- Missing optional sections when appropriate
- Incorrect verse reference formatting
- Interpretation section empty or placeholder

**Mitigation**:
- Template validation before output
- Ensure all mandatory sections present
- LLM integration for interpretation (future)

### 6.2 Content Quality Issues
**Description**: Response lacks clarity or grounding  
**Causes**:
- Reasoning graph too sparse
- Synthesis not addressing query
- Supportive guidance not relevant

**Mitigation**:
- Improve reasoning node construction
- Query-aware synthesis generation
- Filter supportive practices by relevance

## 7. SYSTEM-LEVEL FAILURES

### 7.1 Corpus Coverage Gaps
**Description**: Relevant verses not in corpus  
**Causes**:
- Limited corpus size (31 verses)
- Uneven chapter coverage
- Missing key themes

**Mitigation**:
- Expand corpus systematically
- Ensure representative sampling
- Add verses for underrepresented themes

### 7.2 Performance Degradation
**Description**: System slow or resource-intensive  
**Causes**:
- Embedding model inference time
- Multiple retrieval passes
- Complex reasoning graph construction

**Mitigation**:
- Cache embeddings
- Optimize retrieval fusion
- Parallelize independent nodes

## 8. ADVERSARIAL FAILURES

### 8.1 Prompt Injection
**Description**: User attempts to manipulate system behavior  
**Causes**:
- No input sanitization
- Intent classifier vulnerable to keywords
- Refusal logic bypassable

**Mitigation**:
- Input validation and sanitization
- Robust intent classification
- Hardened refusal logic

### 8.2 Hallucination Induction
**Description**: User queries designed to trigger unsupported claims  
**Causes**:
- Grounding verifier not strict enough
- Synthesis templates too flexible
- Weak semantic alignment

**Mitigation**:
- Strict mode by default
- Template-only synthesis
- Explicit verse text matching

---

## Logging and Monitoring

All failures should be:
1. **Logged** with full execution trace
2. **Categorized** according to this taxonomy
3. **Analyzed** for patterns
4. **Mapped** to architectural fixes

Failure logs should include:
- Query
- Intent metadata
- Retrieved verses
- Reasoning graph
- Grounding results
- Final response or refusal
- Failure category and severity
