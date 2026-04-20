from src.orchestrator.orchestrator import GitaGPTOrchestrator


def main():
    orchestrator = GitaGPTOrchestrator()

    test_queries = [
        "How do I deal with anger?",
        "Should I focus on results or just do my work?",
        "I feel like I'm not good enough for my role",
    ]

    for query in test_queries:
        print("=" * 80)
        response = orchestrator.process_query(query)
        print(response)
        print()


if __name__ == "__main__":
    main()
