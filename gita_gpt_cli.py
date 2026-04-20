import argparse
import sys

from src.orchestrator.orchestrator import GitaGPTOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Gita GPT — Bhagavad Gita Grounded Agentic RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gita_gpt_cli.py "How do I deal with anger?"
  python gita_gpt_cli.py "What is the nature of the self?" --verbose
  python gita_gpt_cli.py --interactive
        """,
    )

    parser.add_argument("query", nargs="?", help="Your question to the Bhagavad Gita")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show execution trace")
    parser.add_argument("-c", "--config", default="config/config.yaml", help="Path to config file")

    args = parser.parse_args()

    try:
        orchestrator = GitaGPTOrchestrator(config_path=args.config)
    except Exception as e:
        print(f"Error initializing Gita GPT: {e}")
        sys.exit(1)

    if args.interactive:
        run_interactive_mode(orchestrator, args.verbose)
    elif args.query:
        response = orchestrator.process_query(args.query, verbose=args.verbose)
        print(response)
    else:
        parser.print_help()
        sys.exit(1)


def run_interactive_mode(orchestrator: GitaGPTOrchestrator, verbose: bool = False):
    print("=" * 80)
    print("Gita GPT — Interactive Mode (v2, Agentic)")
    print("=" * 80)
    print("Commands:")
    print("  'quit' / 'exit' / 'q'  — end the session")
    print("  'trace'                — toggle execution trace")
    print("  'reset'                — clear conversation memory")
    print("  'memory'               — show recent conversation context")
    print("=" * 80)
    print()

    show_trace = verbose

    while True:
        try:
            query = input("\nYour question: ").strip()

            if not query:
                continue

            if query.lower() in ("quit", "exit", "q"):
                print("\nOm Shanti. May you find peace and clarity.")
                break

            if query.lower() == "trace":
                show_trace = not show_trace
                print(f"Execution trace {'enabled' if show_trace else 'disabled'}")
                continue

            if query.lower() == "reset":
                orchestrator.reset_memory()
                print("Conversation memory cleared.")
                continue

            if query.lower() == "memory":
                print("\n--- Recent conversation context ---")
                print(orchestrator.conversation_memory.summary())
                print("-----------------------------------")
                continue

            print()
            response = orchestrator.process_query(query, verbose=show_trace)
            print(response)

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Om Shanti.")
            break
        except Exception as e:
            print(f"\nError processing query: {e}")
            if show_trace:
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()
