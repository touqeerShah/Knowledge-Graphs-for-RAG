"""Backwards-compatible runner for the separate knowledge-graph labs.

Each lab now lives in src/labs/lab_XX_*.py. Run one lab with:

    python3 src/contructing-knowlwdge-graph.py --lab 3

Or run the complete sequence with --lab all.
"""

from __future__ import annotations

import argparse
import sys

from labs.lab_01_inspect_data import run as lab_1
from labs.lab_02_chunk_text import run as lab_2
from labs.lab_03_create_chunk_nodes import run as lab_3
from labs.lab_04_connect_graph import run as lab_4
from labs.lab_05_create_embeddings import run as lab_5
from labs.lab_06_rag_with_ollama import run as lab_6
from labs.lab_07_add_investment_graph import run as lab_7
from labs.lab_08_graph_enriched_rag import run as lab_8

LABS = {
    1: lab_1, 2: lab_2, 3: lab_3, 4: lab_4,
    5: lab_5, 6: lab_6, 7: lab_7, 8: lab_8,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a knowledge graph + RAG learning lab.")
    parser.add_argument("--lab", choices=[*(str(number) for number in LABS), "all"], default="1")
    args = parser.parse_args()
    selected = LABS.values() if args.lab == "all" else (LABS[int(args.lab)],)
    try:
        for lab in selected:
            lab()
    except RuntimeError as error:
        print(f"\nSetup error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
