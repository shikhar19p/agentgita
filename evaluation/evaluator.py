import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field

from src.orchestrator.orchestrator import GitaGPTOrchestrator
from src.core.state import SystemState


@dataclass
class EvaluationMetrics:
    retrieval_recall_at_k: float = 0.0
    citation_precision: float = 0.0
    hallucination_rate: float = 0.0
    refusal_accuracy: float = 0.0
    
    total_queries: int = 0
    correct_refusals: int = 0
    incorrect_refusals: int = 0
    
    retrieval_results: List[Dict[str, Any]] = field(default_factory=list)
    citation_results: List[Dict[str, Any]] = field(default_factory=list)
    hallucination_results: List[Dict[str, Any]] = field(default_factory=list)


class GitaGPTEvaluator:
    
    def __init__(self, orchestrator: GitaGPTOrchestrator, test_cases_path: str):
        self.orchestrator = orchestrator
        self.test_cases = self._load_test_cases(test_cases_path)
        self.metrics = EvaluationMetrics()
    
    def _load_test_cases(self, path: str) -> List[Dict[str, Any]]:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_evaluation(self, k: int = 5) -> EvaluationMetrics:
        print("=" * 80)
        print("GITA GPT EVALUATION")
        print("=" * 80)
        print(f"Running {len(self.test_cases)} test cases...\n")
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"[{i}/{len(self.test_cases)}] {test_case['id']}: {test_case['query']}")
            self._evaluate_test_case(test_case, k)
        
        self._calculate_aggregate_metrics()
        
        return self.metrics
    
    def _evaluate_test_case(self, test_case: Dict[str, Any], k: int):
        query = test_case['query']
        
        state = SystemState(query=query, active_query=query)

        state = self.orchestrator.intent_classifier.classify(state)
        
        should_refuse = test_case['should_refuse']
        actually_refused = state.intent.requires_refusal
        
        if should_refuse == actually_refused:
            self.metrics.correct_refusals += 1
        else:
            self.metrics.incorrect_refusals += 1
        
        if should_refuse:
            print(f"  ✓ Correctly identified as requiring refusal")
            self.metrics.total_queries += 1
            return
        
        state = self.orchestrator.hybrid_retriever.retrieve(state)
        
        expected_verses = set(test_case.get('expected_verses', []))
        retrieved_verses = set(rv.verse_id for rv in state.retrieved_verses[:k])
        
        if expected_verses:
            recall = len(expected_verses.intersection(retrieved_verses)) / len(expected_verses)
            self.metrics.retrieval_results.append({
                'test_id': test_case['id'],
                'recall': recall,
                'expected': list(expected_verses),
                'retrieved': list(retrieved_verses)
            })
            print(f"  Retrieval Recall@{k}: {recall:.2f}")
        
        state = self.orchestrator.contradiction_detector.detect(state)
        state = self.orchestrator.dialectical_reasoner.reason(state)
        state = self.orchestrator.grounding_verifier.verify(state)
        
        cited_verses = set()
        for node in state.reasoning_graph:
            cited_verses.update(node.supporting_verses)
        
        if cited_verses:
            valid_citations = cited_verses.intersection(set(rv.verse_id for rv in state.retrieved_verses))
            precision = len(valid_citations) / len(cited_verses)
            
            self.metrics.citation_results.append({
                'test_id': test_case['id'],
                'precision': precision,
                'cited': list(cited_verses),
                'valid': list(valid_citations)
            })
            print(f"  Citation Precision: {precision:.2f}")
        
        ungrounded_claims = sum(1 for node in state.reasoning_graph if not node.grounded)
        total_claims = len(state.reasoning_graph)
        
        if total_claims > 0:
            hallucination_rate = ungrounded_claims / total_claims
            self.metrics.hallucination_results.append({
                'test_id': test_case['id'],
                'hallucination_rate': hallucination_rate,
                'ungrounded': ungrounded_claims,
                'total': total_claims
            })
            print(f"  Hallucination Rate: {hallucination_rate:.2f}")
        
        self.metrics.total_queries += 1
        print()
    
    def _calculate_aggregate_metrics(self):
        if self.metrics.retrieval_results:
            avg_recall = sum(r['recall'] for r in self.metrics.retrieval_results) / len(self.metrics.retrieval_results)
            self.metrics.retrieval_recall_at_k = avg_recall
        
        if self.metrics.citation_results:
            avg_precision = sum(r['precision'] for r in self.metrics.citation_results) / len(self.metrics.citation_results)
            self.metrics.citation_precision = avg_precision
        
        if self.metrics.hallucination_results:
            avg_hallucination = sum(r['hallucination_rate'] for r in self.metrics.hallucination_results) / len(self.metrics.hallucination_results)
            self.metrics.hallucination_rate = avg_hallucination
        
        total_refusal_tests = self.metrics.correct_refusals + self.metrics.incorrect_refusals
        if total_refusal_tests > 0:
            self.metrics.refusal_accuracy = self.metrics.correct_refusals / total_refusal_tests
    
    def print_report(self):
        print("=" * 80)
        print("EVALUATION REPORT")
        print("=" * 80)
        print(f"\nTotal Queries Evaluated: {self.metrics.total_queries}")
        print(f"\nRetrieval Recall@K: {self.metrics.retrieval_recall_at_k:.3f}")
        print(f"Citation Precision: {self.metrics.citation_precision:.3f}")
        print(f"Hallucination Rate: {self.metrics.hallucination_rate:.3f}")
        print(f"Refusal Accuracy: {self.metrics.refusal_accuracy:.3f}")
        print(f"  - Correct Refusals: {self.metrics.correct_refusals}")
        print(f"  - Incorrect Refusals: {self.metrics.incorrect_refusals}")
        print("\n" + "=" * 80)
    
    def save_results(self, output_path: str):
        results = {
            'summary': {
                'total_queries': self.metrics.total_queries,
                'retrieval_recall_at_k': self.metrics.retrieval_recall_at_k,
                'citation_precision': self.metrics.citation_precision,
                'hallucination_rate': self.metrics.hallucination_rate,
                'refusal_accuracy': self.metrics.refusal_accuracy,
                'correct_refusals': self.metrics.correct_refusals,
                'incorrect_refusals': self.metrics.incorrect_refusals
            },
            'retrieval_results': self.metrics.retrieval_results,
            'citation_results': self.metrics.citation_results,
            'hallucination_results': self.metrics.hallucination_results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")


def main():
    print("Initializing Gita GPT for evaluation...\n")
    orchestrator = GitaGPTOrchestrator()
    
    evaluator = GitaGPTEvaluator(
        orchestrator=orchestrator,
        test_cases_path='evaluation/test_cases.json'
    )
    
    metrics = evaluator.run_evaluation(k=5)
    
    evaluator.print_report()
    
    evaluator.save_results('evaluation/evaluation_results.json')


if __name__ == "__main__":
    main()
