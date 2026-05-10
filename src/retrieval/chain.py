import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from src.retrieval.retriever import get_retriever

load_dotenv()

_CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
    """Dado o histórico da conversa e uma pergunta de acompanhamento, reformule a pergunta
para ser independente e autocontida, preservando o contexto necessário. Responda apenas com a
pergunta reformulada, sem explicações adicionais.

Histórico da conversa:
{chat_history}

Pergunta de acompanhamento: {question}

Pergunta reformulada:"""
)

_QA_PROMPT = PromptTemplate(
    template="""Você é um assistente jurídico especialista na Consolidação das Leis do Trabalho \
(CLT) brasileira.

Diretrizes:
- Responda com base exclusivamente nos trechos da CLT fornecidos abaixo.
- Cite sempre o número do artigo (ex: "Conforme o Art. 134 da CLT, ...") quando disponível.
- Use linguagem clara e acessível; explique termos técnicos sempre que necessário.
- Se os trechos não contiverem a informação solicitada, informe claramente: \
"Não encontrei essa informação nos trechos da CLT disponíveis."
- Nunca invente, presuma ou extrapole informações além do que está nos trechos.
- Quando a resposta envolver prazos, valores ou percentuais, destaque-os explicitamente.

Trechos da CLT:
{context}

Pergunta: {question}

Resposta:""",
    input_variables=["context", "question"],
)

_chain: ConversationalRetrievalChain | None = None


def build_chain() -> ConversationalRetrievalChain:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2,
    )
    retriever = get_retriever(k=6)
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        condense_question_prompt=_CONDENSE_QUESTION_PROMPT,
        combine_docs_chain_kwargs={"prompt": _QA_PROMPT},
        return_source_documents=False,
        verbose=False,
    )


def get_answer(question: str, chat_history: list[tuple[str, str]]) -> str:
    """Consulta a CLT e retorna uma resposta textual.

    Args:
        question: Pergunta do usuário.
        chat_history: Histórico como lista de tuplas (pergunta_humano, resposta_assistente).
    """
    global _chain
    if _chain is None:
        _chain = build_chain()
    result = _chain.invoke({"question": question, "chat_history": chat_history})
    return result["answer"]
