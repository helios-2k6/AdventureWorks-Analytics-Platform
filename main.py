# Main entry point for AdventureWorks Analytics Platform

"""Entry point for the platform. This file is intentionally thin and delegates
real orchestration to the application layer."""

from src.app.app import App


def main():
    """Launch the application through the app layer."""
    app = App()
    return app.run()


if __name__ == "__main__":
    main()
