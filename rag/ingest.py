#!/usr/bin/env python3
"""
ingest.py — build the local vector store from a folder of markdown notes.

Usage:
    python3 ingest.py <path-to-vault> [--out ./index]

Example (this project's Obsidian vault):
    python3 ingest.py "/path/to/Agentic Knowledge Graph/wiki" --out ./index
"""

import argparse
from pathlib import Path

from rag_lib import TfidfIndex, load_and_chunk_vault


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault", type=Path, help="Directory of markdown files to index (recursive)")
    parser.add_argument("--out", type=Path, default=Path("./index"), help="Where to write the vector store")
    args = parser.parse_args()

    if not args.vault.exists():
        raise SystemExit(f"Vault path does not exist: {args.vault}")

    print(f"Loading + chunking markdown under: {args.vault}")
    chunks = load_and_chunk_vault(args.vault)
    print(f"  {len(chunks)} chunks from {len(set(c.doc_path for c in chunks))} documents")

    print("Fitting TF-IDF index...")
    index = TfidfIndex().fit(chunks)
    print(f"  vocabulary size: {len(index.vocab)}")

    index.save(args.out)
    print(f"Saved vector store to: {args.out.resolve()}")
    print("  - vectors.npz  (embeddings + IDF weights)")
    print("  - chunks.json  (chunk text + citations)")


if __name__ == "__main__":
    main()
