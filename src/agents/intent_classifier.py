from typing import Dict, Any
import re
from src.core.state import SystemState, IntentMetadata, Domain, Complexity, RefusalReason


class IntentClassifier:
    
    DOMAIN_KEYWORDS = {
        Domain.ETHICAL: [
            "duty", "right", "wrong", "should", "moral", "ethics", "dharma",
            "responsibility", "obligation", "virtue", "sin", "good", "bad"
        ],
        Domain.THEOLOGICAL: [
            "god", "divine", "krishna", "brahman", "atman", "soul", "spirit",
            "worship", "devotion", "bhakti", "prayer", "faith", "belief"
        ],
        Domain.PRACTICAL: [
            "how to", "what should i", "how can i", "dealing with", "manage",
            "handle", "cope", "practice", "apply", "do", "action", "work"
        ],
        Domain.METAPHYSICAL: [
            "reality", "existence", "nature of", "what is", "consciousness",
            "self", "truth", "illusion", "maya", "real", "unreal", "being"
        ]
    }
    
    OUT_OF_SCOPE_PATTERNS = [
        r'\b(stock|market|trading|investment|money|finance)\b',
        r'\b(recipe|cooking|food|diet|nutrition)\b',
        r'\b(sports|game|match|score)\b',
        r'\b(movie|film|entertainment|celebrity)\b',
        r'\b(politics|election|government|party)\b',
        r'\b(technology|software|computer|app|website)\b',
        r'\b(medical|disease|symptom|treatment|medicine)\b',
        r'\b(weight|height|age|physical|body|appearance|looks)\b',
        r'\b(my brother|my sister|my mother|my father|my family|my friend)\b.*\b(weight|height|age)\b',
    ]
    
    COMPLEXITY_INDICATORS = {
        Complexity.SIMPLE: [
            "what is", "define", "meaning of", "who is", "when"
        ],
        Complexity.MODERATE: [
            "how", "why", "explain", "difference between", "relationship"
        ],
        Complexity.COMPLEX: [
            "reconcile", "contradiction", "paradox", "multiple", "various",
            "different perspectives", "schools of thought", "interpretations"
        ]
    }
    
    def __init__(self):
        pass
    
    def classify(self, state: SystemState) -> SystemState:
        state.add_trace("INTENT_CLASSIFICATION", "Starting intent classification")
        
        query_lower = state.query.lower()
        
        if self._is_out_of_scope(query_lower):
            state.intent.domain = Domain.OUT_OF_SCOPE
            state.intent.requires_refusal = True
            state.intent.refusal_reason = RefusalReason.OUT_OF_SCOPE
            state.intent.confidence = 0.9
            state.add_trace("INTENT_CLASSIFICATION", f"Classified as OUT_OF_SCOPE")
            return state
        
        domain = self._classify_domain(query_lower)
        state.intent.domain = domain
        
        complexity = self._classify_complexity(query_lower)
        state.intent.complexity = complexity
        
        confidence = self._calculate_confidence(query_lower, domain)
        state.intent.confidence = confidence
        
        state.add_trace("INTENT_CLASSIFICATION", 
                       f"Domain: {domain.value}, Complexity: {complexity.value}, Confidence: {confidence:.2f}")
        
        return state
    
    def _is_out_of_scope(self, query: str) -> bool:
        for pattern in self.OUT_OF_SCOPE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    def _classify_domain(self, query: str) -> Domain:
        domain_scores = {domain: 0 for domain in Domain if domain != Domain.OUT_OF_SCOPE}
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    domain_scores[domain] += 1
        
        if all(score == 0 for score in domain_scores.values()):
            return Domain.PRACTICAL
        
        max_domain = max(domain_scores.items(), key=lambda x: x[1])
        return max_domain[0]
    
    def _classify_complexity(self, query: str) -> Complexity:
        for complexity, indicators in self.COMPLEXITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in query:
                    return complexity
        
        word_count = len(query.split())
        if word_count <= 5:
            return Complexity.SIMPLE
        elif word_count <= 15:
            return Complexity.MODERATE
        else:
            return Complexity.COMPLEX
    
    def _calculate_confidence(self, query: str, domain: Domain) -> float:
        if domain == Domain.OUT_OF_SCOPE:
            return 0.9
        
        keywords = self.DOMAIN_KEYWORDS.get(domain, [])
        matches = sum(1 for kw in keywords if kw in query)
        
        if matches == 0:
            return 0.3
        elif matches == 1:
            return 0.5
        elif matches == 2:
            return 0.7
        else:
            return 0.9
