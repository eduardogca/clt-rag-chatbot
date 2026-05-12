import json
import os
import time

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.retrieval.vectorstore import load_vectorstore

load_dotenv()

_JUDGE_PROMPT = ChatPromptTemplate.from_template(
    """Avalie se o trecho da CLT abaixo é relevante para responder à pergunta.

Pergunta: {question}

Trecho (artigo: {artigo}):
{chunk}

Responda APENAS com um JSON no formato: {{"score": X}}
X é um inteiro entre 0 e 3:
- 0: irrelevante
- 1: pouco relevante (menciona o tema mas não responde diretamente)
- 2: relevante (contém informação útil para responder)
- 3: muito relevante (responde diretamente à pergunta)

JSON:"""
)

_llm: ChatGoogleGenerativeAI | None = None
_vs = None


def _get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        # gemini-1.5-flash: ~1500 req/dia no free tier vs 20 do gemini-2.5-flash
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.0,
        )
    return _llm


def _get_vs():
    global _vs
    if _vs is None:
        _vs = load_vectorstore()
    return _vs


def score_cosine(query: str, docs: list[Document]) -> list[float]:
    """Returns relevance scores (0–1) from ChromaDB for each doc.

    Uses similarity_search_with_relevance_scores so no extra embedding call
    is needed beyond what ChromaDB already computed during retrieval.
    """
    vs = _get_vs()
    k = max(len(docs), 1)
    scored = vs.similarity_search_with_relevance_scores(query, k=k)
    lookup = {r[0].page_content[:100]: r[1] for r in scored}
    return [max(0.0, lookup.get(d.page_content[:100], 0.0)) for d in docs]


def score_llm(query: str, docs: list[Document]) -> list[float]:
    """Returns LLM-as-judge scores normalized to 0–1 (raw 0–3 divided by 3).

    Retries up to 3 times on 429 rate-limit errors with exponential backoff.
    """
    llm = _get_llm()
    chain = _JUDGE_PROMPT | llm | StrOutputParser()
    scores = []
    for doc in docs:
        score = 0.0
        for attempt in range(3):
            try:
                raw = chain.invoke({
                    "question": query,
                    "artigo": doc.metadata.get("artigo", "desconhecido"),
                    "chunk": doc.page_content[:800],
                })
                start, end = raw.find("{"), raw.rfind("}") + 1
                data = json.loads(raw[start:end])
                score = min(max(int(data["score"]), 0), 3) / 3.0
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    wait = 15 * (2 ** attempt)
                    print(f"    Rate limit no LLM-judge, aguardando {wait}s...")
                    time.sleep(wait)
                else:
                    break
        scores.append(score)
    return scores


def evaluate_chunks(query: str, docs: list[Document]) -> list[dict]:
    """Evaluates relevance of each chunk with cosine similarity + LLM-as-judge.

    Returns list sorted by combined score (descending). Each item:
        {
            "doc": Document,
            "cosine": float,      # 0–1, from ChromaDB distance
            "llm_score": float,   # 0–1, from LLM judge (raw 0-3 / 3)
            "combined": float,    # 0.4 * cosine + 0.6 * llm_score
        }
    """
    cosine_scores = score_cosine(query, docs)
    llm_scores = score_llm(query, docs)
    evaluated = [
        {
            "doc": doc,
            "cosine": round(c, 3),
            "llm_score": round(l, 3),
            "combined": round(0.4 * c + 0.6 * l, 3),
        }
        for doc, c, l in zip(docs, cosine_scores, llm_scores)
    ]
    return sorted(evaluated, key=lambda x: x["combined"], reverse=True)
