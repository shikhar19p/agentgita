from src.orchestrator.orchestrator import GitaGPTOrchestrator

print("=" * 80)
print("TESTING LLM INTEGRATION")
print("=" * 80)
print()

orchestrator = GitaGPTOrchestrator()

test_queries = [
    "How do I deal with anger?",
    "Should I focus on results or just do my work?",
    "What is the nature of the self?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'=' * 80}")
    print(f"TEST {i}/{len(test_queries)}")
    print(f"{'=' * 80}\n")
    
    response = orchestrator.process_query(query, verbose=False)
    print(response)
    print()
