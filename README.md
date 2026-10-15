## Knowledge Graphs for RAG

This project is a set of small labs for learning how to:

1. inspect a filing and split it into useful chunks;
2. store chunks and metadata as Neo4j nodes;
3. connect chunks with `PART_OF`, `SECTION`, and `NEXT` relationships;
4. create local embeddings with Ollama;
5. compare vector RAG with graph-window RAG; and
6. connect a 10-K filing to Form 13 investment data.

The labs are now split into separate files under [`src/labs/`](src/labs/):

- `lab_01_inspect_data.py` — inspect the filing
- `lab_02_chunk_text.py` — split text and preserve metadata
- `lab_03_create_chunk_nodes.py` — create Neo4j chunk nodes
- `lab_04_connect_graph.py` — create graph relationships
- `lab_05_create_embeddings.py` — create Ollama embeddings
- `lab_06_rag_with_ollama.py` — compare vector and graph-window RAG
- `lab_07_add_investment_graph.py` — add Form 13 entities
- `lab_08_graph_enriched_rag.py` — combine graph facts with retrieved text

[`src/contructing-knowlwdge-graph.py`](src/contructing-knowlwdge-graph.py) remains as a backwards-compatible runner. The filename keeps the original spelling so existing course links continue to work.

### Setup

Install the project dependencies:

```bash
uv sync
```

If you are running the examples with the system `python3` command shown below,
install the project into that Python environment instead:

```bash
python3 -m pip install -e .
```

Install and start [Ollama](https://ollama.com), then download the default models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

Create a `.env` file in the repository root:

```dotenv
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2
OLLAMA_EMBED_MODEL=nomic-embed-text
VECTOR_DIMENSIONS=768
```

`VECTOR_DIMENSIONS` must match the embedding model. `nomic-embed-text` normally produces 768-dimensional vectors.

### Run the labs

Start with the local-only labs:

```bash
python3 src/contructing-knowlwdge-graph.py --lab 1
python3 src/contructing-knowlwdge-graph.py --lab 2
```

Then run the Neo4j pipeline in order:

```bash
python3 src/contructing-knowlwdge-graph.py --lab 3
python3 src/contructing-knowlwdge-graph.py --lab 4
python3 src/contructing-knowlwdge-graph.py --lab 5
python3 src/contructing-knowlwdge-graph.py --lab 6
python3 src/contructing-knowlwdge-graph.py --lab 7
python3 src/contructing-knowlwdge-graph.py --lab 8
```

Every lab prints its purpose before executing. Labs 3–8 are idempotent for the provided data, so they can be repeated while learning. `--lab all` runs every lab in order.

You can also run an individual file directly, for example:

```bash
python3 src/labs/lab_01_inspect_data.py
python3 src/labs/lab_02_chunk_text.py
```

### Important Neo4j note

Lab 6's graph-window query uses `apoc.text.join`, so APOC must be available in the Neo4j database. If APOC is unavailable, use Lab 6's plain retriever first or replace that query with a client-side document join.
