"""Interactive console assistant for generating user stories and test cases."""

from __future__ import annotations

import textwrap

from .chat_agent import EpicChatAgent


def run_cli() -> None:
    """Run the interactive loop until the user quits."""

    agent = EpicChatAgent()
    print("👋  Hi! I'm your Agile planning assistant. Type 'help' for options.")
    while True:
        try:
            prompt = input("you> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Goodbye!")
            return

        response = agent.respond(prompt)
        print("assistant>")
        print(textwrap.indent(response.content, prefix="  "))

        if response.content.endswith("close the program now.") or prompt.lower() in {"exit", "quit", "bye"}:
            return


if __name__ == "__main__":
    run_cli()