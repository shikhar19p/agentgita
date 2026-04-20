import re
from typing import List
from src.core.state import SystemState, Domain


class QueryReformulator:
    """
    Reformulates weak queries before a retrieval retry.

    Strategy: expand with domain synonyms and drop noise words.
    Does not call an LLM — deterministic and fast.
    """

    _DOMAIN_EXPANSIONS = {
        Domain.ETHICAL: ["dharma", "duty", "right action", "moral"],
        Domain.THEOLOGICAL: ["Krishna", "divine", "Brahman", "bhakti"],
        Domain.PRACTICAL: ["practice", "apply", "daily life", "how"],
        Domain.METAPHYSICAL: ["self", "atma", "reality", "consciousness"],
    }

    _STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "of", "in", "on", "at", "to", "for", "with", "by", "from",
        "up", "about", "into", "through", "during", "before", "after",
        "above", "below", "between", "out", "off", "over", "under",
        "again", "further", "then", "once", "me", "my", "myself", "i",
    }

    def reformulate(self, state: SystemState, attempt: int) -> str:
        original = state.query
        domain = state.intent.domain

        # Strip stop words for a more focused query
        words = re.findall(r'\b\w+\b', original.lower())
        content_words = [w for w in words if w not in self._STOP_WORDS]

        # Add domain-specific expansions on second attempt
        expansions: List[str] = []
        if attempt >= 2 and domain and domain in self._DOMAIN_EXPANSIONS:
            expansions = self._DOMAIN_EXPANSIONS[domain][:2]

        reformulated = " ".join(content_words + expansions)
        state.add_trace(
            "QUERY_REFORMULATOR",
            f"Attempt {attempt}: '{original}' → '{reformulated}'"
        )
        return reformulated
