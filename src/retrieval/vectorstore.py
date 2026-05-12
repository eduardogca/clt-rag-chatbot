import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from src.ingestion.embedder import GeminiEmbeddings

load_dotenv()

# Raiz do projeto: src/retrieval/vectorstore.py → ../../.. = project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_vectorstore(persist_dir: str = "data/vectorstore") -> Chroma:
    persist_path = Path(persist_dir)
    if not persist_path.is_absolute():
        persist_path = _PROJECT_ROOT / persist_dir
    embeddings = GeminiEmbeddings(api_key=os.getenv("GOOGLE_API_KEY"))
    return Chroma(persist_directory=str(persist_path), embedding_function=embeddings)
