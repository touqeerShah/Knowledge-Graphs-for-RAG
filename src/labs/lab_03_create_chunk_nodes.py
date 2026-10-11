"""Lab 3: create Chunk nodes and a uniqueness constraint."""
try:
    from .common import get_graph, split_form10k, print_lab
except ImportError:
    from common import get_graph, split_form10k, print_lab

def run() -> None:
    print_lab(3, "Create Chunk nodes", """
        MERGE is idempotent: running this lab twice does not duplicate a
        chunk. The unique constraint protects chunkId and makes future imports
        safe. This lab stores text and metadata, but not embeddings yet.
    """)
    kg = get_graph()
    chunks = split_form10k()
    kg.query("CREATE CONSTRAINT unique_chunk IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE")
    kg.query("""
        UNWIND $chunks AS chunk
        MERGE (c:Chunk {chunkId: chunk.chunkId})
        SET c += chunk
    """, params={"chunks": chunks})
    print(kg.query("MATCH (c:Chunk) RETURN count(c) AS chunks"))

if __name__ == "__main__":
    run()
