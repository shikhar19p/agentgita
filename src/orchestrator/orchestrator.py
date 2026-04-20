import yaml
from pathlib import Path
from typing import Dict, Any

from src.core.state import SystemState
from src.core.corpus_validator import CorpusLoader
from src.agents.intent_classifier import IntentClassifier
from src.retrieval.hybrid_retriever import HybridRetriever
from src.agents.contradiction_detector import ContradictionDetector
from src.agents.dialectical_reasoner import DialecticalReasoner
from src.agents.grounding_verifier import GroundingVerifier
from src.agents.plurality_checker import PluralityChecker
from src.rendering.response_renderer import ResponseRenderer
from src.rendering.refusal_handler import RefusalHandler
from src.llm.openai_client import OpenAIClient
from src.llm.gemini_client import GeminiClient
from src.llm.interpretation_generator import InterpretationGenerator


class GitaGPTOrchestrator:
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        
        self.corpus_loader = None
        self.intent_classifier = None
        self.hybrid_retriever = None
        self.contradiction_detector = None
        self.dialectical_reasoner = None
        self.grounding_verifier = None
        self.plurality_checker = None
        self.response_renderer = None
        self.refusal_handler = None
        self.openai_client = None
        self.interpretation_generator = None
        
        self._initialize_components()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _initialize_components(self):
        print("Initializing Gita GPT components...")
        
        corpus_path = self.config['corpus']['path']
        self.corpus_loader = CorpusLoader(
            corpus_path,
            strict_validation=self.config['corpus']['validation']['strict_schema']
        )
        self.corpus_loader.load()
        print(f"✓ Loaded {len(self.corpus_loader.corpus)} verses")
        
        self.intent_classifier = IntentClassifier()
        print("✓ Intent classifier initialized")
        
        dense_weight = self.config['retrieval']['hybrid']['dense_weight']
        sparse_weight = self.config['retrieval']['hybrid']['sparse_weight']
        top_k = self.config['retrieval']['hybrid']['top_k']
        context_expansion = self.config['retrieval']['hybrid']['context_expansion']
        neighbor_verses = self.config['retrieval']['hybrid']['neighbor_verses']
        
        self.hybrid_retriever = HybridRetriever(
            dense_weight=dense_weight,
            sparse_weight=sparse_weight,
            top_k=top_k,
            context_expansion=context_expansion,
            neighbor_verses=neighbor_verses
        )
        self.hybrid_retriever.index_corpus(self.corpus_loader.corpus)
        print("✓ Hybrid retriever indexed")
        
        self.contradiction_detector = ContradictionDetector()
        print("✓ Contradiction detector initialized")
        
        self.dialectical_reasoner = DialecticalReasoner()
        print("✓ Dialectical reasoner initialized")
        
        strict_grounding = self.config['reasoning']['grounding']['strict_mode']
        self.grounding_verifier = GroundingVerifier(strict_mode=strict_grounding)
        print("✓ Grounding verifier initialized")
        
        self.plurality_checker = PluralityChecker()
        print("✓ Plurality checker initialized")
        
        self.response_renderer = ResponseRenderer()
        print("✓ Response renderer initialized")
        
        self.refusal_handler = RefusalHandler()
        print("✓ Refusal handler initialized")
        
        try:
            llm_provider = self.config['reasoning']['llm'].get('provider', 'openai')
            llm_model = self.config['reasoning']['llm']['model']
            llm_temp = self.config['reasoning']['llm']['temperature']
            llm_max_tokens = self.config['reasoning']['llm']['max_tokens']
            
            if llm_provider == 'gemini':
                llm_client = GeminiClient(
                    model=llm_model,
                    temperature=llm_temp,
                    max_tokens=llm_max_tokens
                )
                print(f"✓ LLM integration initialized (Gemini: {llm_model})")
            else:
                llm_client = OpenAIClient(
                    model=llm_model,
                    temperature=llm_temp,
                    max_tokens=llm_max_tokens
                )
                print(f"✓ LLM integration initialized (OpenAI: {llm_model})")
            
            self.openai_client = llm_client
            self.interpretation_generator = InterpretationGenerator(llm_client)
        except Exception as e:
            print(f"⚠ LLM integration skipped: {e}")
            print("  System will use template-based interpretation")
            self.openai_client = None
            self.interpretation_generator = None
        
        print("\nGita GPT ready.\n")
    
    def process_query(self, query: str, verbose: bool = False) -> str:
        state = SystemState(query=query)
        state.add_trace("ORCHESTRATOR", "Starting query processing")
        
        state = self.intent_classifier.classify(state)
        
        if state.intent.requires_refusal:
            state = self.refusal_handler.handle_refusal(state)
            if verbose:
                self._print_execution_trace(state)
            return state.final_response
        
        state = self.hybrid_retriever.retrieve(state)
        
        if not state.retrieved_verses:
            state.refusal_reason = state.core.state.RefusalReason.INSUFFICIENT_GROUNDING
            state = self.refusal_handler.handle_refusal(state)
            if verbose:
                self._print_execution_trace(state)
            return state.final_response
        
        state = self.contradiction_detector.detect(state)
        
        state = self.dialectical_reasoner.reason(state)
        
        state = self.grounding_verifier.verify(state)
        
        if state.should_refuse():
            state = self.refusal_handler.handle_refusal(state)
            if verbose:
                self._print_execution_trace(state)
            return state.final_response
        
        if self.interpretation_generator:
            state = self.interpretation_generator.generate(state)
        
        state = self.plurality_checker.check(state)
        
        state = self.response_renderer.render(state)
        
        state.add_trace("ORCHESTRATOR", "Query processing complete")
        
        if verbose:
            self._print_execution_trace(state)
        
        return state.final_response
    
    def _print_execution_trace(self, state: SystemState):
        print("\n" + "=" * 80)
        print("EXECUTION TRACE")
        print("=" * 80)
        for trace in state.execution_trace:
            print(trace)
        print("=" * 80 + "\n")
