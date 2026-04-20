from src.load_corpus import load_corpus
from src.verse_selector import select_verse
from src.response_builder import build_response


def main():
    corpus = load_corpus()
    print(f"Loaded {len(corpus)} verses from corpus\n")
    
    test_queries = [
        "How do I deal with anger?",
        "Should I focus on results or just do my work?",
        "I feel like I'm not good enough for my role"
    ]
    
    for query in test_queries:
        print("=" * 80)
        selected_verse = select_verse(query, corpus)
        response = build_response(query, selected_verse)
        print(response)
        print()


if __name__ == "__main__":
    main()
