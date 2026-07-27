#!/usr/bin/env python3
"""
query.py — retrieve the top-k most relevant chunks for a question.

Usage:
    python3 query.py "what is loop engineering?" [--k 5] [--index ./index]

This only performs *retrieval* (steps 4-6 of the pipeline in rag_lib.py).
It deliberately does not call an LLM to generate an answer — that's the
"G" in RAG, and bolting it on is one line (send the printed context block
+ the question to the Claude API / claude -p). Keeping retrieval and
generation as separate, inspectable steps makes it obvious what the model
is (and isn't) grounded on, which is the entire point of building this by
hand instead of importing a framework.
"""

import argparse
import textwrap
from pathlib import Path

from rag_lib import TfidfIndex


def format_result(chunk, score: int, rank: int) -> str:
    header = f"[{rank}] {chunk.doc_title}  ›  {chunk.heading}   (score={score:.3f})"
    citation = f"    source: {chunk.doc_path}"
    body = textwrap.indent(textwrap.fill(chunk.text, width=88), "    ")
    return f"{header}\n{citation}\n{body}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Natural-language question")
    parser.add_argument("--k", type=int, default=5, help="Number of chunks to retrieve")
    parser.add_argument("--index", type=Path, default=Path("./index"), help="Vector store directory")
    args = parser.parse_args()

    if not (args.index / "vectors.npz").exists():
        raise SystemExit(f"No index found at {args.index}. Run ingest.py first.")

    index = TfidfIndex.load(args.index)
    results = index.search(args.query, k=args.k)

    print(f'Query: "{args.query}"')
    print(f"Retrieved {len(results)} chunk(s) from {len(index.chunks)} indexed chunks\n")

    if not results:
        print("No matches. Try different terms, or lower the score threshold in rag_lib.search().")
        return

    for rank, (chunk, score) in enumerate(results, start=1):
        print(format_result(chunk, score, rank))

    print("--- Context block (what you'd paste to an LLM alongside the question) ---")
    context = "\n\n".join(f"[{c.doc_title} › {c.heading}] ({c.doc_path})\n{c.text}" for c, _ in results)
    print(context)


if __name__ == "__main__":
    main()
