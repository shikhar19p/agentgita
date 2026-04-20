import argparse
import sys
from pathlib import Path

from src.orchestrator.orchestrator import GitaGPTOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Gita GPT - Bhagavad Gita Grounded Agentic RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gita_gpt_cli.py "How do I deal with anger?"
  python gita_gpt_cli.py "What is the nature of the self?" --verbose
  python gita_gpt_cli.py --interactive
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Your question to the Bhagavad Gita'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Start interactive mode'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show execution trace'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
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
    print("Gita GPT - Interactive Mode")
    print("=" * 80)
    print("Ask questions about the Bhagavad Gita.")
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'trace' to toggle execution trace display.")
    print("=" * 80)
    print()
    
    show_trace = verbose
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nOm Shanti. May you find peace and clarity.")
                break
            
            if query.lower() == 'trace':
                show_trace = not show_trace
                status = "enabled" if show_trace else "disabled"
                print(f"Execution trace {status}")
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
