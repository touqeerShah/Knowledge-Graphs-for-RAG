"""Lab 6: compare plain vector RAG with graph-window RAG."""
try:
    from .common import get_ollama_chat, vector_retriever, print_lab
except ImportError:
    from common import get_ollama_chat, vector_retriever, print_lab

def run() -> None:
    from langchain_core.prompts import ChatPromptTemplate
    print_lab(6, "Compare plain RAG with graph-window RAG", """
        The first retriever returns the nearest chunks. The second uses NEXT
        relationships to add one neighbour on either side of each match. The
        same local Ollama chat model then answers from the retrieved context.
    """)
    plain = vector_retriever()
    window_query = """
        MATCH (left)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(right)
        WITH node, score, collect(DISTINCT left.text) + collect(DISTINCT node.text) + collect(DISTINCT right.text) AS parts
        RETURN apoc.text.join(parts, '\\n') AS text, score, node {.source, .chunkId} AS metadata
    """
    windowed = vector_retriever(window_query)
    prompt = ChatPromptTemplate.from_template(
        "Answer using only the context. If it is absent, say you do not know.\\n\\n"
        "Context:\\n{context}\\n\\nQuestion: {question}"
    )
    question = "In one sentence, what is NetApp's business?"
    for name, retriever in (("plain", plain), ("graph window", windowed)):
        docs = retriever.invoke(question)
        context = "\\n\\n".join(doc.page_content for doc in docs)
        answer = (prompt | get_ollama_chat()).invoke({"context": context, "question": question})
        print(f"\\n{name} answer:\\n{answer.content}")

if __name__ == "__main__":
    run()
