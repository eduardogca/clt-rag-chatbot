import re
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

MAX_CHUNK_SIZE = 1500  # artigos muito longos são subdivididos


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def chunk_by_article(text: str) -> list[dict]:
    """
    Splits CLT text into chunks by article (Art. X).
    Returns list of {"text": ..., "artigo": "Art. X", "secao": "TÍTULO I..."}.
    Long articles are further split with overlap, keeping the article reference.
    """
    pattern = re.compile(r"(?=^Art\.\s+\d+[\w\-]*)", re.MULTILINE)
    parts = pattern.split(text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_SIZE,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )

    # Matches section headings but NOT table-of-contents lines (which have dots)
    titulo_pattern = re.compile(
        r"^(TÍTULO|CAPÍTULO|SEÇÃO|Título|Capítulo|Seção)\s+[^\n\.]{3,}$", re.MULTILINE
    )
    current_secao = "Introdução"
    chunks = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Update current section heading if found (skip TOC lines with dots)
        for match in titulo_pattern.finditer(part):
            heading = match.group(0).strip()
            if "....." not in heading:
                current_secao = heading
                break

        # Extract article number from the first line
        artigo_match = re.match(r"(Art\.\s+\d+[\w\-]*)", part)
        artigo = artigo_match.group(1) if artigo_match else None

        # Skip preamble chunks (no article number = editorial intro, not CLT content)
        if artigo is None:
            continue

        if len(part) <= MAX_CHUNK_SIZE:
            chunks.append({"text": part, "artigo": artigo, "secao": current_secao})
        else:
            # Subdivide long articles keeping metadata
            sub_chunks = splitter.split_text(part)
            for sub in sub_chunks:
                chunks.append({
                    "text": sub,
                    "artigo": artigo,
                    "secao": current_secao,
                })

    return chunks


# Keep backward-compatible function for notebooks/tests that import chunk_text
def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "Art.", " ", ""],
    )
    return splitter.split_text(text)


if __name__ == "__main__":
    text = load_text("data/processed/clt.txt")
    chunks = chunk_by_article(text)
    print(f"Total chunks: {len(chunks)}")
    print(f"\nExample chunk:")
    print(f"  artigo : {chunks[10]['artigo']}")
    print(f"  secao  : {chunks[10]['secao']}")
    print(f"  texto  : {chunks[10]['text'][:200]}...")
