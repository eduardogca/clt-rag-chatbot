from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "Art.", " ", ""],
    )
    return splitter.split_text(text)


if __name__ == "__main__":
    text = load_text("data/processed/clt.txt")
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")
    print(f"\nExample chunk:\n{chunks[0]}")
