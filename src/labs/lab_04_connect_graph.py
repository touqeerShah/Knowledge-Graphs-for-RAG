"""Lab 4: connect chunks, sections, and filings."""
try:
    from .common import DEFAULT_SEC_FILE, get_graph, read_sec_json, print_lab
except ImportError:
    from common import DEFAULT_SEC_FILE, get_graph, read_sec_json, print_lab

def run() -> None:
    print_lab(4, "Connect chunks, sections, and filings", """
        A vector store answers similarity questions. A graph adds structure:
        chunks belong to a Form, each section points to its first chunk, and
        NEXT relationships preserve reading order. This lets us retrieve a
        neighbouring context window instead of an isolated passage.
    """)
    kg = get_graph()
    filing = read_sec_json()
    params = {"formId": DEFAULT_SEC_FILE.stem}
    params.update({k: filing.get(k, "") for k in ("names", "source", "cik", "cusip6")})
    kg.query("""
        MERGE (f:Form {formId: $formId})
        SET f.names = $names, f.source = $source, f.cik = $cik, f.cusip6 = $cusip6
    """, params=params)
    kg.query("""
        MATCH (c:Chunk {formId: $formId}), (f:Form {formId: $formId})
        MERGE (c)-[:PART_OF]->(f)
    """, params={"formId": DEFAULT_SEC_FILE.stem})
    kg.query("""
        MATCH (a:Chunk {formId: $formId}), (b:Chunk {formId: $formId})
        WHERE a.f10kItem = b.f10kItem AND b.chunkSeqId = a.chunkSeqId + 1
        MERGE (a)-[:NEXT]->(b)
    """, params={"formId": DEFAULT_SEC_FILE.stem})
    kg.query("""
        MATCH (first:Chunk {formId: $formId}), (f:Form {formId: $formId})
        WHERE first.chunkSeqId = 0
        MERGE (f)-[:SECTION {f10kItem: first.f10kItem}]->(first)
    """, params={"formId": DEFAULT_SEC_FILE.stem})
    print(kg.query("MATCH (a)-[r]->(b) RETURN type(r) AS relationship, count(*) AS total"))

if __name__ == "__main__":
    run()
