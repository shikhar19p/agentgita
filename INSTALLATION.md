# Gita GPT - Installation & Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 2GB free disk space (for embedding models)
- Internet connection (for first-time model download)

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd "c:\Users\Satya Krishna\OneDrive\Desktop\gita_gpt"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- sentence-transformers (for dense retrieval)
- rank-bm25 (for sparse retrieval)
- scikit-learn (for similarity calculations)
- pyyaml (for configuration)
- openai (for future LLM integration)
- python-dotenv (for environment variables)

**Note:** First installation will download ~400MB of embedding models.

### 3. Verify Installation

```bash
python test_corpus.py
```

Expected output:
```
================================================================================
CORPUS VALIDATION REPORT
================================================================================

⚠ WARNINGS: 1
  [BG_14_22] interpretive_notes.scope: Scope 'philosical' not in valid scopes...

================================================================================

Corpus Stats:
{
  "total_verses": 31,
  "chapters_covered": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
  ...
}
```

## Quick Start

### Single Query Mode

```bash
python gita_gpt_cli.py "How do I deal with anger?"
```

### Interactive Mode

```bash
python gita_gpt_cli.py --interactive
```

Commands in interactive mode:
- Type your question and press Enter
- Type `trace` to toggle execution trace
- Type `quit` or `exit` to end session

### With Execution Trace (Debugging)

```bash
python gita_gpt_cli.py "What is the nature of the self?" --verbose
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
retrieval:
  hybrid:
    dense_weight: 0.6    # Adjust semantic search weight
    sparse_weight: 0.4   # Adjust keyword search weight
    top_k: 5             # Number of verses to retrieve

reasoning:
  grounding:
    strict_mode: true    # Refuse if any claim is ungrounded
```

## Running Evaluation

```bash
python evaluation/evaluator.py
```

This will:
- Run 10 test cases
- Calculate retrieval recall, citation precision, hallucination rate
- Generate evaluation report
- Save results to `evaluation/evaluation_results.json`

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Solution:**
```bash
pip install sentence-transformers
```

### Issue: Model download fails

**Solution:**
- Check internet connection
- Try manual download:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Issue: "FileNotFoundError: Corpus file not found"

**Solution:**
- Ensure you're in the project root directory
- Verify `data/corpus.json` exists

### Issue: Slow first query

**Explanation:** First query loads embedding model into memory (~5-10 seconds). Subsequent queries are fast.

## System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 2GB

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB
- Storage: 5GB
- GPU: Optional (speeds up embedding inference)

## Next Steps

1. Read `README.md` for usage examples
2. Review `GITA_GPT_SYSTEM_DOCUMENTATION.md` for architecture details
3. Explore `evaluation/test_cases.json` for example queries
4. Check `evaluation/failure_taxonomy.md` for known limitations

## Support

For issues or questions:
1. Check `GITA_GPT_SYSTEM_DOCUMENTATION.md`
2. Review execution trace with `--verbose` flag
3. Check `evaluation/failure_taxonomy.md` for known issues

---

**Om Shanti** 🙏
