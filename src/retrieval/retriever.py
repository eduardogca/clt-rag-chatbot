from vectorstore import load_vectorstore


def get_retriever(k: int = 5):
    vectorstore = load_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": k})
