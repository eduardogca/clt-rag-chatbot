import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from chunker import load_text, chunk_text

load_dotenv()


def build_vectorstore(chunks: list[str], persist_dir: str = "data/vectorstore") -> Chroma:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    return vectorstore


if __name__ == "__main__":
    text = load_text("data/processed/clt.txt")
    chunks = chunk_text(text)
    print(f"Generating embeddings for {len(chunks)} chunks...")
    vectorstore = build_vectorstore(chunks)
    print(f"Vectorstore saved to data/vectorstore/")
