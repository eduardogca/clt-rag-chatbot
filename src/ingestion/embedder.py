import os
import time
import requests
from typing import List
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from src.ingestion.chunker import load_text, chunk_by_article

load_dotenv()

MODEL = "models/gemini-embedding-001"
BATCH_SIZE = 5
DELAY_BETWEEN_BATCHES = 12  # seconds — stays under 5 RPM free tier limit
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
PROGRESS_FILE = "data/vectorstore/.progress"


class GeminiEmbeddings(Embeddings):
    """REST client for Gemini embedding models (v1beta endpoint)."""

    def __init__(self, api_key: str, model: str = MODEL):
        self.api_key = api_key
        self.model = model

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        payload = {
            "requests": [
                {"model": self.model, "content": {"parts": [{"text": t}]}}
                for t in texts
            ]
        }
        for attempt in range(10):
            resp = requests.post(
                f"{BASE_URL}/{self.model}:batchEmbedContents",
                params={"key": self.api_key},
                json=payload,
                timeout=60,
            )
            if resp.status_code == 429:
                wait = min(2 ** attempt * 15, 300)
                print(f"    Rate limit hit, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return [item["values"] for item in resp.json()["embeddings"]]
        resp.raise_for_status()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        result = []
        for i in range(0, len(texts), BATCH_SIZE):
            result.extend(self._embed_batch(texts[i : i + BATCH_SIZE]))
        return result

    def embed_query(self, text: str) -> List[float]:
        return self._embed_batch([text])[0]


def _read_progress() -> int:
    try:
        return int(open(PROGRESS_FILE).read().strip())
    except Exception:
        return 0


def _save_progress(batch_index: int) -> None:
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    open(PROGRESS_FILE, "w").write(str(batch_index))


def build_vectorstore(chunks: List[dict], persist_dir: str = "data/vectorstore") -> Chroma:
    embeddings = GeminiEmbeddings(api_key=os.getenv("GOOGLE_API_KEY"))
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )
    texts = [c["text"] for c in chunks]
    metadatas = [{"artigo": c["artigo"], "secao": c["secao"]} for c in chunks]

    total_batches = -(-len(texts) // BATCH_SIZE)
    start_batch = _read_progress()

    if start_batch > 0:
        print(f"Resuming from batch {start_batch + 1}/{total_batches} ({start_batch * BATCH_SIZE} chunks already done)")

    for i in range(start_batch * BATCH_SIZE, len(texts), BATCH_SIZE):
        batch_texts = texts[i : i + BATCH_SIZE]
        batch_meta = metadatas[i : i + BATCH_SIZE]
        vectorstore.add_texts(batch_texts, metadatas=batch_meta)
        batch_num = i // BATCH_SIZE + 1
        _save_progress(batch_num)
        print(f"  Batch {batch_num}/{total_batches} done ({i + len(batch_texts)}/{len(texts)} chunks)")
        time.sleep(DELAY_BETWEEN_BATCHES)

    return vectorstore


if __name__ == "__main__":
    text = load_text("data/processed/clt.txt")
    chunks = chunk_by_article(text)
    print(f"Generating embeddings for {len(chunks)} chunks...")
    vectorstore = build_vectorstore(chunks)
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
    print(f"Vectorstore saved to data/vectorstore/")
