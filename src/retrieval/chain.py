import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from src.retrieval.retriever import get_retriever

load_dotenv()

PROMPT_TEMPLATE = """Você é um assistente especialista na Consolidação das Leis do Trabalho (CLT) brasileira.
Use apenas os trechos da CLT fornecidos abaixo para responder à pergunta.
Se a informação não estiver nos trechos, diga que não encontrou a informação na CLT.
Seja claro, objetivo e cite o artigo quando possível.

Trechos da CLT:
{context}

Pergunta: {question}

Resposta:"""


def build_chain() -> RetrievalQA:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2,
    )
    prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])
    retriever = get_retriever(k=5)
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
    )


if __name__ == "__main__":
    chain = build_chain()
    answer = chain.invoke({"query": "Quantos dias de férias o trabalhador tem direito?"})
    print(answer["result"])
