"""Lab 8: add graph facts to retrieved text before asking Ollama."""
try:
    from .common import get_graph, get_ollama_chat, vector_retriever, print_lab
except ImportError:
    from common import get_graph, get_ollama_chat, vector_retriever, print_lab

def run() -> None:
    print_lab(8, "Use graph facts to enrich retrieved text", """
        Retrieval can return both a text chunk and facts connected to that
        chunk. Here Cypher finds investors linked through the chunk's Form;
        the result is added to the LLM context before asking Ollama to answer.
    """)
    kg = get_graph()
    docs = vector_retriever().invoke("Who owns shares in the company described by this filing?")
    if not docs:
        print("No chunks found. Run labs 3-5 first.")
        return
    chunk_id = docs[0].metadata.get("chunkId")
    facts = kg.query("""
        MATCH (c:Chunk {chunkId: $chunkId})-[:PART_OF]->(:Form)<-[:FILED]-(company:Company)
        OPTIONAL MATCH (manager:Manager)-[owns:OWNS_STOCK_IN]->(company)
        RETURN manager.managerName + ' owns ' + toString(owns.shares) + ' shares in ' + company.companyName AS fact
        LIMIT 10
    """, params={"chunkId": chunk_id})
    graph_context = "\\n".join(row["fact"] for row in facts if row.get("fact"))
    text_context = "\\n\\n".join(doc.page_content for doc in docs)
    answer = get_ollama_chat().invoke(
        "Answer from the filing text and graph facts. Cite no unsupported facts.\\n"
        f"Filing text:\\n{text_context}\\n\\nGraph facts:\\n{graph_context}"
        "\\n\\nQuestion: Who owns shares in the company described by this filing?"
    )
    print(answer.content)

if __name__ == "__main__":
    run()
