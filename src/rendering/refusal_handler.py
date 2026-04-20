from typing import Dict, Any
from src.core.state import SystemState, RefusalReason


class RefusalHandler:
    
    REFUSAL_TEMPLATES = {
        RefusalReason.OUT_OF_SCOPE: {
            "title": "Question Outside Bhagavad Gita Scope",
            "explanation": "The Bhagavad Gita primarily addresses questions of dharma (duty), self-knowledge, devotion, and the nature of reality. Your question appears to be outside this scope.",
            "suggestion": "If you have a question about ethics, purpose, inner conflict, or spiritual understanding, please feel free to ask."
        },
        RefusalReason.INSUFFICIENT_GROUNDING: {
            "title": "Insufficient Grounding in Verses",
            "explanation": "While the Gita may touch upon themes related to your question, I cannot construct a response that is fully grounded in specific verses without risk of overreach or misrepresentation.",
            "suggestion": "You might try rephrasing your question more specifically, or asking about a particular aspect that the Gita directly addresses."
        },
        RefusalReason.CONTRADICTORY_EVIDENCE: {
            "title": "Multiple Contradictory Perspectives",
            "explanation": "The verses relevant to your question present perspectives that appear contradictory without sufficient context for synthesis. The Gita contains dialectical teachings that require careful interpretation.",
            "suggestion": "Consider asking about specific verses or concepts, or how different paths (karma yoga, bhakti yoga, jnana yoga) relate to your question."
        },
        RefusalReason.AMBIGUOUS_INTENT: {
            "title": "Ambiguous Question",
            "explanation": "Your question could be interpreted in multiple ways, and I want to ensure I provide a response grounded in the appropriate verses.",
            "suggestion": "Please clarify your question or provide more context about what aspect you're interested in."
        }
    }
    
    def __init__(self):
        pass
    
    def handle_refusal(self, state: SystemState) -> SystemState:
        state.add_trace("REFUSAL_HANDLER", "Generating refusal response")
        
        refusal_reason = state.refusal_reason or state.intent.refusal_reason
        
        if refusal_reason is None or refusal_reason == RefusalReason.NONE:
            state.add_trace("REFUSAL_HANDLER", "No refusal needed")
            return state
        
        template = self.REFUSAL_TEMPLATES.get(refusal_reason)
        
        if not template:
            template = self.REFUSAL_TEMPLATES[RefusalReason.OUT_OF_SCOPE]
        
        refusal_response = self._construct_refusal_response(
            state.query,
            template,
            refusal_reason
        )
        
        state.final_response = refusal_response
        state.add_trace("REFUSAL_HANDLER", f"Refusal generated: {refusal_reason.value}")
        
        return state
    
    def _construct_refusal_response(self, 
                                   query: str, 
                                   template: Dict[str, str],
                                   reason: RefusalReason) -> str:
        parts = []
        
        parts.append("User Query:")
        parts.append(query)
        parts.append("")
        parts.append("=" * 80)
        parts.append("")
        
        parts.append(f"**{template['title']}**")
        parts.append("")
        
        parts.append(template['explanation'])
        parts.append("")
        
        parts.append(template['suggestion'])
        parts.append("")
        
        parts.append("=" * 80)
        parts.append("")
        parts.append("Note: The Bhagavad Gita is a sacred text addressing eternal questions of")
        parts.append("dharma, self-realization, and devotion. I aim to provide responses that")
        parts.append("are faithful to the text and grounded in specific verses.")
        
        return "\n".join(parts)
