"""Main entry point for interactive CLI with dependency checking."""

import sys

def main():
    """Entry point for interactive CLI with fallback."""
    # Check for Rich availability
    try:
        import rich
        RICH_AVAILABLE = True
    except ImportError:
        RICH_AVAILABLE = False
    
    if RICH_AVAILABLE:
        print("🎨 Starting Rich Interactive Mode...")
        try:
            from .interactive import InteractiveCLI
            cli = InteractiveCLI()
            cli.run()
        except Exception as e:
            print(f"❌ Rich interactive mode failed: {e}")
            print("Falling back to simple mode...")
            from .simple_interactive import main
            main()
    else:
        print("⚠️  Rich library not available. Using simple interactive mode...")
        print("For better experience, install: pip install rich")
        from .simple_interactive import main
        main()


if __name__ == "__main__":
    main()