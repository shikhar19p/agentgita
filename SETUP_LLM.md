# LLM Integration Setup Guide

## Overview

Gita GPT now uses **GPT-4o** (OpenAI's latest model) for generating nuanced, grounded interpretations of Bhagavad Gita verses.

## Setup Steps

### 1. Install/Update Dependencies

```bash
pip install --upgrade openai python-dotenv
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

**Option A: Using .env file (Recommended)**

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Option B: Using environment variable**

Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"
```

Windows (Command Prompt):
```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

Linux/Mac:
```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Verify Setup

```bash
python test_llm_integration.py
```

Expected output:
- System initializes with "✓ LLM integration initialized (model: gpt-4o)"
- Generates interpretations for 3 test queries
- Each response includes LLM-generated interpretation section

## How It Works

### LLM Usage (Strict Boundaries)

**LLM is used ONLY for:**
- Generating interpretation text
- Applying verse teachings to user's specific question
- Nuanced phrasing and explanation

**LLM is NEVER used for:**
- Verse selection (done by hybrid retrieval)
- Verse generation or invention
- Translation or Sanskrit text
- Citation decisions (done by grounding verifier)

### Grounding Safeguards

1. **Strict System Prompt**
   - Explicit rules against invention
   - Citation requirements
   - Grounding boundaries

2. **Verse Context Provided**
   - Only retrieved verses sent to LLM
   - Full verse text, translation, core teaching
   - Supporting verses for context

3. **Post-Generation Verification**
   - Grounding verifier checks LLM output
   - Claims must align with verse text
   - Ungrounded interpretations rejected

4. **Low Temperature (0.3)**
   - Reduces randomness
   - More deterministic outputs
   - Closer adherence to verse text

### Configuration

Edit `config/config.yaml`:

```yaml
reasoning:
  llm:
    provider: "openai"
    model: "gpt-4o"           # Latest OpenAI model
    temperature: 0.3          # Low for consistency
    max_tokens: 1500          # Interpretation length limit
```

**Available Models:**
- `gpt-4o` - Latest, fastest, most capable (recommended)
- `gpt-4-turbo` - Previous generation
- `gpt-4` - Original GPT-4

## Cost Considerations

**GPT-4o Pricing (as of Jan 2026):**
- Input: ~$2.50 per 1M tokens
- Output: ~$10.00 per 1M tokens

**Typical Query Cost:**
- Input: ~500 tokens (verse + prompt)
- Output: ~300 tokens (interpretation)
- Cost per query: ~$0.004 (less than half a cent)

**Monthly estimates:**
- 100 queries: ~$0.40
- 1,000 queries: ~$4.00
- 10,000 queries: ~$40.00

## Fallback Behavior

If LLM integration fails (no API key, network error, etc.):
- System continues with template-based interpretation
- Warning message displayed: "⚠ LLM integration skipped"
- All other features work normally

## Testing

### Quick Test

```bash
python gita_gpt_cli.py "How do I deal with anger?"
```

Look for:
- Interpretation section with detailed, query-specific text
- No placeholder "[Interpretation requires LLM integration]"
- Grounded claims citing verse IDs

### Verbose Test (See LLM in Action)

```bash
python gita_gpt_cli.py "What is the nature of the self?" --verbose
```

Execution trace will show:
```
[INTERPRETATION_GENERATION] Starting LLM-based interpretation
[INTERPRETATION_GENERATION] Generated interpretation (XXX chars)
```

### Interactive Testing

```bash
python gita_gpt_cli.py --interactive
```

Try various questions and observe interpretation quality.

## Troubleshooting

### Error: "OPENAI_API_KEY not found"

**Solution:** Set API key in `.env` file or environment variable (see Step 2 above)

### Error: "Rate limit exceeded"

**Solution:** 
- Wait a few minutes
- Check your OpenAI account usage limits
- Consider upgrading OpenAI plan if needed

### Error: "Invalid API key"

**Solution:**
- Verify API key is correct (starts with `sk-`)
- Check key hasn't expired
- Generate new key at platform.openai.com

### Warning: "LLM integration skipped"

**Causes:**
- No API key configured
- Network connectivity issue
- OpenAI service unavailable

**Impact:** System uses template-based interpretation (still functional)

### Interpretation seems generic

**Check:**
- Temperature setting (should be 0.3)
- Verse retrieval quality (use `--verbose`)
- Query clarity

## System Prompt

The LLM receives this strict system prompt:

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
```

Full prompt in: `src/llm/openai_client.py`

## Security

**Best Practices:**
- Never commit `.env` file to version control
- Use `.gitignore` to exclude `.env`
- Rotate API keys periodically
- Monitor usage on OpenAI dashboard
- Set spending limits in OpenAI account

## Monitoring

**Track in OpenAI Dashboard:**
- Token usage per request
- Daily/monthly costs
- Error rates
- Response times

**Local Logging:**
- Execution traces show LLM calls
- Character counts logged
- Errors captured in trace

---

**Ready to use!** The system now generates high-quality, grounded interpretations using GPT-4o while maintaining all safety constraints.
