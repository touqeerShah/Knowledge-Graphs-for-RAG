"""Lab 1: inspect the source filing."""
import textwrap
try:
    from .common import read_sec_json, print_lab
except ImportError:  # Allows: python3 src/labs/lab_01_inspect_data.py
    from common import read_sec_json, print_lab

def run() -> None:
    print_lab(1, "Inspect the source filing", """
        Before creating graph nodes, understand the shape of the source data.
        A JSON filing contains named sections. We start with Item 1 (the
        business description), because it is useful for a first RAG example.
    """)
    filing = read_sec_json()
    print("Available fields:", ", ".join(filing))
    item1 = filing.get("item1", "")
    print(f"Item 1 characters: {len(item1):,}")
    print("Preview:\n", textwrap.fill(item1[:800], 90))

if __name__ == "__main__":
    run()
