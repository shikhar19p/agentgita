import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from src.core.state import SystemState, Complexity, RefusalReason, ReasoningNode
from src.core.corpus_validator import CorpusLoader
from src.agents.intent_classifier import IntentClassifier
from src.agents.query_reformulator import QueryReformulator
from src.agents.contradiction_detector import ContradictionDetector
from src.agents.dialectical_reasoner import DialecticalReasoner
from src.agents.grounding_verifier import GroundingVerifier
from src.agents.plurality_checker import PluralityChecker
from src.retrieval.hybrid_retriever import HybridRetriever
from src.rendering.response_renderer import ResponseRenderer
from src.rendering.refusal_handler import RefusalHandler
from src.memory.conversation_memory import ConversationMemory
from src.llm.openai_client import OpenAIClient
from src.llm.gemini_client import GeminiClient
from src.llm.interpretation_generator import InterpretationGenerator

MAX_RETRIEVAL_ATTEMPTS = 3
CONFIDENCE_THRESHOLD = 0.20


class GitaGPTOrchestrator:
    """
    True agentic orchestrator implementing a Reason → Act → Observe → Re-reason loop.

    Key agentic behaviors:
    - Dynamic step selection: skips heavy steps for simple queries.
    - Query reformulation + retry: if retrieval confidence is low the agent rewrites
      the query and retrieves again (up to MAX_RETRIEVAL_ATTEMPTS).
    - Grounding-driven retry: if grounding fails the agent reformulates once more
      before refusing.
    - Episodic conversation memory: follow-up queries are enriched with prior context.
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self._initialize_components()
        self.conversation_memory = ConversationMemory(max_turns=10)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_file) as f:
            return yaml.safe_load(f)

    def _initialize_components(self):
        print("Initializing Gita GPT components...")

        corpus_path = self.config["corpus"]["path"]
        self.corpus_loader = CorpusLoader(
            corpus_path,
            strict_validation=self.config["corpus"]["validation"]["strict_schema"],
        )
        self.corpus_loader.load()
        print(f"✓ Loaded {len(self.corpus_loader.corpus)} verses")

        self.intent_classifier = IntentClassifier()
        self.query_reformulator = QueryReformulator()
        print("✓ Intent classifier + query reformulator initialized")

        cfg = self.config["retrieval"]["hybrid"]
        self.hybrid_retriever = HybridRetriever(
            dense_weight=cfg["dense_weight"],
            sparse_weight=cfg["sparse_weight"],
            top_k=cfg["top_k"],
            context_expansion=cfg["context_expansion"],
            neighbor_verses=cfg["neighbor_verses"],
        )
        self.hybrid_retriever.index_corpus(self.corpus_loader.corpus)
        print("✓ Hybrid retriever (ChromaDB) indexed")

        self.contradiction_detector = ContradictionDetector()
        self.dialectical_reasoner = DialecticalReasoner()
        print("✓ Contradiction detector + dialectical reasoner initialized")

        strict = self.config["reasoning"]["grounding"]["strict_mode"]
        self.grounding_verifier = GroundingVerifier(strict_mode=strict)
        self.plurality_checker = PluralityChecker()
        print("✓ Grounding verifier + plurality checker initialized")

        self.response_renderer = ResponseRenderer()
        self.refusal_handler = RefusalHandler()
        print("✓ Response renderer + refusal handler initialized")

        self._init_llm()
        print("\nGita GPT ready.\n")

    def _init_llm(self):
        try:
            provider = self.config["reasoning"]["llm"].get("provider", "openai")
            model = self.config["reasoning"]["llm"]["model"]
            temp = self.config["reasoning"]["llm"]["temperature"]
            max_tok = self.config["reasoning"]["llm"]["max_tokens"]

            if provider == "gemini":
                client = GeminiClient(model=model, temperature=temp, max_tokens=max_tok)
                print(f"✓ LLM integration initialized (Gemini: {model})")
            else:
                client = OpenAIClient(model=model, temperature=temp, max_tokens=max_tok)
                print(f"✓ LLM integration initialized (OpenAI: {model})")

            self.interpretation_generator: Optional[InterpretationGenerator] = InterpretationGenerator(client)
        except Exception as e:
            print(f"⚠ LLM integration skipped: {e}")
            print("  System will use template-based interpretation")
            self.interpretation_generator = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_query(self, query: str, verbose: bool = False) -> str:
        # Enrich query with episodic memory context for follow-ups
        enriched_query = self.conversation_memory.enrich_query(query)
        state = SystemState(query=query, active_query=enriched_query)
        state.add_trace("ORCHESTRATOR", f"Starting ReAct loop for: '{query}'")

        result = self._react_loop(state)

        # Store turn in episodic memory on success
        if state.final_response and not state.should_refuse():
            themes = []
            for rv in state.retrieved_verses[:3]:
                themes.extend(rv.verse_data.get("themes", []))
            self.conversation_memory.add_turn(
                query=query,
                response=state.final_response[:200],
                verse_ids=[rv.verse_id for rv in state.retrieved_verses],
                themes=list(dict.fromkeys(themes))[:5],
            )

        if verbose:
            self._print_execution_trace(state)

        return result

    def reset_memory(self):
        """Clear conversation history — call between independent sessions."""
        self.conversation_memory.clear()

    # ------------------------------------------------------------------
    # ReAct loop
    # ------------------------------------------------------------------

    def _react_loop(self, state: SystemState) -> str:
        """
        Reason → Act → Observe cycle.

        Phase 1: Reason  — classify intent, plan which steps to skip
        Phase 2: Act     — retrieve with auto-retry on low confidence
        Phase 3: Reason  — decide depth of analysis
        Phase 4: Act     — contradiction detection + reasoning
        Phase 5: Observe — grounding verification; retry on failure
        Phase 6: Render  — format final response
        """

        # ── Phase 1: classify + plan ────────────────────────────────────
        state = self.intent_classifier.classify(state)
        if state.should_refuse():
            return self._refuse(state)

        # Dynamic step selection based on complexity
        run_contradiction = state.intent.complexity in (Complexity.MODERATE, Complexity.COMPLEX)
        run_dialectical = state.intent.complexity == Complexity.COMPLEX

        state.add_trace(
            "ORCHESTRATOR",
            f"Plan: contradiction={run_contradiction}, dialectical={run_dialectical}"
        )

        # ── Phase 2: retrieve with retry ────────────────────────────────
        state = self._retrieval_with_retry(state)
        if state.should_refuse():
            return self._refuse(state)

        # ── Phase 3 & 4: reasoning ──────────────────────────────────────
        if run_contradiction:
            state = self.contradiction_detector.detect(state)

        if run_dialectical:
            state = self.dialectical_reasoner.reason(state)
        else:
            state = self._build_simple_reasoning(state)

        # ── Phase 5: grounding + retry ──────────────────────────────────
        state = self.grounding_verifier.verify(state)

        if state.should_refuse() and state.reformulation_count < MAX_RETRIEVAL_ATTEMPTS:
            # Observe: grounding failed → re-reason with different retrieval
            state.refusal_reason = None
            state.add_trace("ORCHESTRATOR", "Grounding failed — triggering reformulation retry")
            state = self._retrieval_with_retry(state, force_reformulate=True)
            if not state.should_refuse():
                state = self.grounding_verifier.verify(state)

        if state.should_refuse():
            return self._refuse(state)

        # ── Phase 6: LLM + render ───────────────────────────────────────
        if self.interpretation_generator:
            state = self.interpretation_generator.generate(state)

        state = self.plurality_checker.check(state)
        state = self.response_renderer.render(state)
        state.add_trace("ORCHESTRATOR", "ReAct loop complete")
        return state.final_response

    # ------------------------------------------------------------------
    # Retrieval with query reformulation retry
    # ------------------------------------------------------------------

    def _retrieval_with_retry(self, state: SystemState, force_reformulate: bool = False) -> SystemState:
        for attempt in range(1, MAX_RETRIEVAL_ATTEMPTS + 1):
            if attempt > 1 or force_reformulate:
                state.reformulation_count += 1
                reformulated = self.query_reformulator.reformulate(state, attempt)
                state.active_query = reformulated

            state = self.hybrid_retriever.retrieve(state)

            if not state.retrieved_verses:
                state.add_trace("ORCHESTRATOR", f"Attempt {attempt}: no results, retrying")
                continue

            if state.retrieval_confidence_ok(CONFIDENCE_THRESHOLD):
                state.add_trace(
                    "ORCHESTRATOR",
                    f"Retrieval confidence OK ({state.retrieval_confidence:.3f}) on attempt {attempt}"
                )
                return state

            state.add_trace(
                "ORCHESTRATOR",
                f"Attempt {attempt}: low confidence ({state.retrieval_confidence:.3f}), reformulating"
            )

        if not state.retrieved_verses:
            state.refusal_reason = RefusalReason.INSUFFICIENT_GROUNDING
            state.add_trace("ORCHESTRATOR", "All retrieval attempts failed — refusing")
        else:
            state.add_trace(
                "ORCHESTRATOR",
                f"Accepting low-confidence results after {MAX_RETRIEVAL_ATTEMPTS} attempts"
            )
        return state

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_simple_reasoning(self, state: SystemState) -> SystemState:
        """For SIMPLE queries, synthesise a single reasoning node without dialectical agent."""
        if state.retrieved_verses:
            top = state.retrieved_verses[0]
            node = ReasoningNode(
                claim=top.verse_data.get("translation_english", "")[:200],
                supporting_verses=[top.verse_id],
                grounded=True,
                confidence=top.relevance_score,
            )
            state.reasoning_graph.append(node)
            state.mark_step("simple_reasoning")
        return state

    def _refuse(self, state: SystemState) -> str:
        state = self.refusal_handler.handle_refusal(state)
        return state.final_response

    def _print_execution_trace(self, state: SystemState):
        print("\n" + "=" * 80)
        print("EXECUTION TRACE")
        print("=" * 80)
        for trace in state.execution_trace:
            print(trace)
        print(f"\nSteps completed : {state.steps_completed}")
        print(f"Retrieval conf  : {state.retrieval_confidence:.3f}")
        print(f"Reformulations  : {state.reformulation_count}")
        print(f"Conversation mem: {self.conversation_memory.summary()}")
        print("=" * 80 + "\n")
