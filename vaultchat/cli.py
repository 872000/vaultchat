"""VaultChat command-line interface: `chat` loop and one-shot `ask`."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__
from .answer import answer_question
from .ingest import ingest
from .retrieval import build_index, search

DEFAULT_DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "docs")


def build(docs_dir: str, top_k_default: int = 3):
    chunks = ingest(docs_dir)
    index = build_index(chunks)
    return index


def run_query(index, query: str, top_k: int = 3) -> str:
    hits = search(query, index, top_k=top_k)
    answer = answer_question(query, hits)
    return answer.render()


def cmd_ask(args) -> int:
    index = build(args.docs)
    print(run_query(index, args.question, top_k=args.top_k))
    return 0


def cmd_chat(args) -> int:
    index = build(args.docs)
    print(f"VaultChat {__version__} — chatting over {args.docs}")
    print("Ask anything. Type 'exit', 'quit' or press Ctrl-D to leave.\n")
    while True:
        try:
            query = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if query.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        if not query:
            continue
        print()
        print(run_query(index, query, top_k=args.top_k))
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vaultchat",
        description="Chat with your documents — local RAG-lite Q&A with cited sources.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--docs", default=DEFAULT_DOCS_DIR, help="Directory of markdown/text docs")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ask = sub.add_parser("ask", help="Answer a single question and exit")
    p_ask.add_argument("question", help="The question to answer")
    p_ask.add_argument("--top-k", type=int, default=3, help="Chunks to retrieve")
    p_ask.set_defaults(func=cmd_ask)

    p_chat = sub.add_parser("chat", help="Start an interactive chat loop")
    p_chat.add_argument("--top-k", type=int, default=3, help="Chunks to retrieve per question")
    p_chat.set_defaults(func=cmd_chat)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
