from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class Domain(Enum):
    ETHICAL = "ethical"
    THEOLOGICAL = "theological"
    PRACTICAL = "practical"
    METAPHYSICAL = "metaphysical"
    OUT_OF_SCOPE = "out_of_scope"


class Complexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class RefusalReason(Enum):
    OUT_OF_SCOPE = "out_of_scope"
    INSUFFICIENT_GROUNDING = "insufficient_grounding"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    AMBIGUOUS_INTENT = "ambiguous_intent"
    NONE = "none"


@dataclass
class IntentMetadata:
    domain: Optional[Domain] = None
    complexity: Optional[Complexity] = None
    requires_refusal: bool = False
    refusal_reason: Optional[RefusalReason] = None
    confidence: float = 0.0


@dataclass
class RetrievedVerse:
    verse_id: str
    verse_data: Dict[str, Any]
    relevance_score: float
    retrieval_method: str


@dataclass
class Contradiction:
    verse_ids: List[str]
    description: str
    severity: str


@dataclass
class ReasoningNode:
    claim: str
    supporting_verses: List[str]
    grounded: bool
    confidence: float


@dataclass
class GroundingResult:
    claim: str
    is_grounded: bool
    supporting_verse_ids: List[str]
    explanation: str


@dataclass
class SystemState:
    query: str
    intent: IntentMetadata = field(default_factory=IntentMetadata)
    retrieved_verses: List[RetrievedVerse] = field(default_factory=list)
    contradictions: List[Contradiction] = field(default_factory=list)
    reasoning_graph: List[ReasoningNode] = field(default_factory=list)
    grounding_results: List[GroundingResult] = field(default_factory=list)
    refusal_reason: Optional[RefusalReason] = None
    execution_trace: List[str] = field(default_factory=list)
    final_response: Optional[str] = None
    
    def add_trace(self, step: str, details: str = ""):
        trace_entry = f"[{step}] {details}" if details else f"[{step}]"
        self.execution_trace.append(trace_entry)
    
    def should_refuse(self) -> bool:
        return self.intent.requires_refusal or self.refusal_reason is not None
