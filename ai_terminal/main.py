
"""CLI entry point for AI Terminal Assistant."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .assistant import AITerminalAssistant
from .config import Config, load_config


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Terminal Assistant - Execute shell commands using natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ai_terminal "list all files"
  python -m ai_terminal "install pandas" --confirm
  python -m ai_terminal "create a new folder called test" --suggest
        """
    )
    
    parser.add_argument(
        "query",
        type=str,
        help="Natural language description of the command to execute"
    )
    
    parser.add_argument(
        "--suggest", "-s",
        action="store_true",
        help="Only suggest commands, don't execute them"
    )
    
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Execute without asking for confirmation (use with caution)"
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        default="gemini",
        choices=["gemini", "openai", "claude"],
        help="AI provider to use (default: gemini)"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 2.0.0"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point for the CLI application."""
    try:
        args = parse_arguments()
        
       
        config = load_config(args.config)
        
       
        if args.provider:
            config.ai_provider = args.provider
        if args.verbose:
            config.verbose = True
        
       
        assistant = AITerminalAssistant(config)
        
        
        success = assistant.process_query(
            query=args.query,
            suggest_only=args.suggest,
            skip_confirmation=args.no_confirm
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n KeyBoard Interrupt.")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())