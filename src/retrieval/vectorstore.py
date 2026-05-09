import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from src.ingestion.embedder import GeminiEmbeddings

load_dotenv()


def load_vectorstore(persist_dir: str = "data/vectorstore") -> Chroma:
    embeddings = GeminiEmbeddings(api_key=os.getenv("GOOGLE_API_KEY"))
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)
