"""Lab 5: create an Ollama embedding vector index in Neo4j."""
try:
    from .common import VECTOR_DIMENSIONS, get_graph, get_ollama_embeddings, split_form10k, print_lab
except ImportError:
    from common import VECTOR_DIMENSIONS, get_graph, get_ollama_embeddings, split_form10k, print_lab

def run() -> None:
    print_lab(5, "Embed chunks with Ollama", """
        OpenAI's hosted embedding endpoint has been replaced by Ollama. The
        embedding model runs locally, and its vectors are written to Neo4j.
        VECTOR_DIMENSIONS must match the selected embedding model; the default
        (768) matches nomic-embed-text.
    """)
    kg = get_graph()
    chunks = split_form10k()
    embeddings = get_ollama_embeddings().embed_documents([c["text"] for c in chunks])
    kg.query(f"""
        CREATE VECTOR INDEX form_10k_chunks IF NOT EXISTS
        FOR (c:Chunk) ON (c.textEmbedding)
        OPTIONS {{indexConfig: {{
            `vector.dimensions`: {VECTOR_DIMENSIONS},
            `vector.similarity_function`: 'cosine'
        }}}}
    """)
    kg.query("""
        UNWIND $rows AS row
        MATCH (c:Chunk {chunkId: row.chunkId})
        SET c.textEmbedding = row.embedding
    """, params={"rows": [
        {"chunkId": c["chunkId"], "embedding": vector}
        for c, vector in zip(chunks, embeddings)
    ]})
    print(f"Stored {len(embeddings)} Ollama embeddings in Neo4j.")

if __name__ == "__main__":
    run()
