import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.retrieval.retriever import get_retriever

load_dotenv()

_CONDENSE_PROMPT = ChatPromptTemplate.from_template(
    """Dado o histórico da conversa e uma pergunta de acompanhamento, reformule a pergunta
para ser independente e autocontida, preservando o contexto necessário. Responda apenas com a
pergunta reformulada, sem explicações adicionais.

Histórico da conversa:
{chat_history}

Pergunta de acompanhamento: {question}

Pergunta reformulada:"""
)

_QA_PROMPT = ChatPromptTemplate.from_template(
    """Você é um assistente jurídico especialista na Consolidação das Leis do Trabalho \
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

Resposta:"""
)

_llm: ChatGoogleGenerativeAI | None = None
_retriever = None


def _get_components():
    global _llm, _retriever
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2,
        )
    if _retriever is None:
        _retriever = get_retriever(k=6)
    return _llm, _retriever


def get_answer(question: str, chat_history: list[tuple[str, str]]) -> str:
    """Consulta a CLT e retorna uma resposta textual.

    Args:
        question: Pergunta do usuário.
        chat_history: Histórico como lista de tuplas (pergunta_humano, resposta_assistente).
    """
    llm, retriever = _get_components()

    if chat_history:
        formatted_history = "\n".join(
            f"Humano: {h}\nAssistente: {a}" for h, a in chat_history
        )
        question = (_CONDENSE_PROMPT | llm | StrOutputParser()).invoke(
            {"chat_history": formatted_history, "question": question}
        )

    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    return (_QA_PROMPT | llm | StrOutputParser()).invoke(
        {"context": context, "question": question}
    )
