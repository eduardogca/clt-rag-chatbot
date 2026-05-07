import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()


def load_vectorstore(persist_dir: str = "data/vectorstore") -> Chroma:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)
