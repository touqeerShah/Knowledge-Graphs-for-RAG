"""Shared configuration and helpers used by the individual labs."""

from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*_args: Any, **_kwargs: Any) -> bool:
        return False

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "src" / "data"
DEFAULT_SEC_FILE = DATA_DIR / "0000950170-23-027948.json"
DEFAULT_FORM13_FILE = DATA_DIR / "form13.csv"

load_dotenv(ROOT / ".env", override=True)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "2000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
VECTOR_INDEX_NAME = "form_10k_chunks"
VECTOR_DIMENSIONS = int(os.getenv("VECTOR_DIMENSIONS", "768"))


def read_sec_json(path: Path = DEFAULT_SEC_FILE) -> dict[str, Any]:
    """Read one SEC filing exported as JSON."""
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def make_text_splitter():
    """Use LangChain's splitter, with a small fallback for Labs 1-2."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ModuleNotFoundError:
        class SimpleTextSplitter:
            def split_text(self, value: str) -> list[str]:
                step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
                return [value[start:start + CHUNK_SIZE] for start in range(0, len(value), step)]
        return SimpleTextSplitter()
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, length_function=len
    )


def split_form10k(path: Path = DEFAULT_SEC_FILE) -> list[dict[str, Any]]:
    """Split useful 10-K sections and attach metadata to every chunk."""
    filing = read_sec_json(path)
    splitter = make_text_splitter()
    chunks: list[dict[str, Any]] = []
    for section in ("item1", "item1a", "item7", "item7a"):
        text = filing.get(section, "")
        if not text:
            print(f"Skipping missing section: {section}")
            continue
        section_chunks = splitter.split_text(text)[:20]
        for sequence, chunk_text in enumerate(section_chunks):
            chunks.append({
                "chunkId": f"{path.stem}-{section}-chunk{sequence:04d}",
                "formId": path.stem, "f10kItem": section, "chunkSeqId": sequence,
                "text": chunk_text, "names": filing.get("names", ""),
                "cik": filing.get("cik", ""), "cusip6": filing.get("cusip6", ""),
                "source": filing.get("source", str(path)),
            })
        print(f"{section}: {len(section_chunks)} chunks")
    return chunks


def get_graph():
    """Connect to Neo4j using values from .env."""
    from langchain_community.graphs import Neo4jGraph
    required = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing {', '.join(missing)} in .env")
    return Neo4jGraph(
        url=os.environ["NEO4J_URI"], username=os.environ["NEO4J_USERNAME"],
        password=os.environ["NEO4J_PASSWORD"],
        database=os.getenv("NEO4J_DATABASE", "neo4j"),
    )


def get_ollama_embeddings():
    from langchain_ollama import OllamaEmbeddings
    return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL, base_url=OLLAMA_BASE_URL)


def get_ollama_chat():
    from langchain_ollama import ChatOllama
    return ChatOllama(model=OLLAMA_CHAT_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)


def print_lab(number: int, title: str, explanation: str) -> None:
    print(f"\n{'=' * 72}\nLAB {number}: {title}\n{'=' * 72}")
    print(textwrap.fill(" ".join(explanation.split()), 72))


def vector_retriever(retrieval_query: str | None = None):
    """Open the existing Neo4j vector index as a LangChain retriever."""
    from langchain_community.vectorstores import Neo4jVector
    store = Neo4jVector.from_existing_index(
        embedding=get_ollama_embeddings(), url=os.environ["NEO4J_URI"],
        username=os.environ["NEO4J_USERNAME"], password=os.environ["NEO4J_PASSWORD"],
        database=os.getenv("NEO4J_DATABASE", "neo4j"), index_name=VECTOR_INDEX_NAME,
        text_node_property="text",
        retrieval_query=retrieval_query or
        "RETURN node.text AS text, score, node {.source, .chunkId} AS metadata",
    )
    return store.as_retriever(search_kwargs={"k": 4})
