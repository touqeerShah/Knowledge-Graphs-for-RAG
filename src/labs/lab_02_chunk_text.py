"""Lab 2: split text and preserve metadata."""
import textwrap
try:
    from .common import split_form10k, print_lab
except ImportError:
    from common import split_form10k, print_lab

def run() -> None:
    print_lab(2, "Split text into searchable chunks", """
        Vector search works better on focused passages than on one enormous
        filing. Each chunk keeps metadata so retrieval can later show which
        filing, section, and sequence position produced an answer.
    """)
    chunks = split_form10k()
    print(f"Total chunks: {len(chunks)}")
    if chunks:
        print("First chunk metadata:", {k: v for k, v in chunks[0].items() if k != "text"})
        print("First chunk preview:\n", textwrap.fill(chunks[0]["text"][:500], 90))

if __name__ == "__main__":
    run()
