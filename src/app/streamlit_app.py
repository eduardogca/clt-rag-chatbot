import re
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import streamlit as st
from src.retrieval.agent import get_agent_answer_with_sources
from src.retrieval.chain import get_answer_with_sources
# ── Página ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Assistente CLT",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

:root {
    --bg:           #f5f0e8;
    --surface:      #fdf9f3;
    --surface2:     #ede8de;
    --border:       #d6cfc2;
    --accent:       #9a7230;
    --accent-light: #c9a84c;
    --accent-bg:    #fdf3dc;
    --text:         #2c2416;
    --text-muted:   #7a6e5e;
    --user-bg:      #e8f0e8;
    --user-border:  #b8cfb8;
}

/* ── Reset geral ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Título ── */
h1 {
    font-family: 'Lora', serif !important;
    color: var(--accent) !important;
}

/* ── App background ── */
.stApp {
    background-color: var(--bg) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

.sidebar-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.9rem;
    font-size: 0.84rem;
    line-height: 1.75;
}
.sidebar-card b {
    color: var(--accent);
    font-family: 'Lora', serif;
    display: block;
    margin-bottom: 0.35rem;
}
.sidebar-card ul {
    margin: 0;
    padding-left: 1.1rem;
    color: var(--text-muted);
}

/* ── Botões ── */
.stButton > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: background 0.2s !important;
}
.stButton > button:hover {
    background: var(--border) !important;
}

/* ── Badge de modo agêntico ── */
.mode-badge {
    display: inline-block;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.18rem 0.6rem;
    border-radius: 4px;
    background: var(--accent-bg);
    color: var(--accent);
    border: 1px solid var(--accent-light);
    margin-bottom: 1rem;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Badge de modo simples ── */
.mode-badge-simple {
    display: inline-block;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.18rem 0.6rem;
    border-radius: 4px;
    background: var(--surface2);
    color: var(--text-muted);
    border: 1px solid var(--border);
    margin-bottom: 1rem;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Mensagem de boas-vindas ── */
.welcome {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    color: var(--text-muted);
    font-size: 0.95rem;
    line-height: 1.75;
}
.welcome .icon { font-size: 2.2rem; margin-bottom: 0.6rem; }

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text) !important;
    background: transparent !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Esconder elementos padrão ── */
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 760px !important; }
</style>
""", unsafe_allow_html=True)


# ── Funções auxiliares ────────────────────────────────────────────────────────

def _normalize_artigo(text: str) -> str:
    """Extrai o identificador canônico de um artigo: número + sufixo letra."""
    m = re.search(r'(\d+)[º°]?(-[A-Za-z])?', text)
    if not m:
        return ""
    return m.group(1) + (m.group(2) or "").upper()


def _inject_tooltips(text: str, sources: list[dict]) -> str:
    """Envolve menções a artigos (Art. XXX) em <span> com tooltip nativo HTML."""
    if not sources:
        return text

    source_map: dict[str, str] = {}
    for s in sources:
        key = _normalize_artigo(s.get("artigo", ""))
        if key:
            source_map[key] = s["content"]

    def replace(m: re.Match) -> str:
        full = m.group(0)
        key = _normalize_artigo(full)
        if key not in source_map:
            return full
        content = source_map[key]
        snippet = content[:200] + ("..." if len(content) > 200 else "")
        snippet = snippet.replace("\n", " ").replace('"', "&quot;").replace("'", "&#39;")
        return (
            f'<span title="{snippet}" style="border-bottom:1px dotted var(--accent);'
            f"cursor:help;color:var(--accent);font-weight:500;\">{full}</span>"
        )

    return re.sub(r'\b[Aa]rt\.\s*\d+[º°]?(?:-[A-Z])?\b', replace, text)


def _render_sources_expander(sources: list[dict]) -> None:
    with st.expander(f"📖 Artigos da CLT consultados ({len(sources)})"):
        for s in sources:
            st.markdown(f"**{s['artigo']}**")
            snippet = s["content"]
            if len(snippet) > 300:
                snippet = snippet[:300] + "..."
            st.markdown(snippet)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚖️ CLT Assistente")
    st.caption("Chatbot RAG · NLP 6º Semestre")
    st.divider()

    agentic_mode = st.toggle("Modo agêntico", value=True, key="agentic_mode")
    st.caption(
        "Agêntico: avalia relevância e reformula query. "
        "Simples: mais rápido, menos chamadas à API."
    )
    show_sources = st.toggle("Mostrar artigos utilizados", value=True, key="show_sources")

    st.divider()

    st.markdown("""
    <div class="sidebar-card">
        <b>💡 Exemplos de perguntas</b>
        <ul>
            <li>Quantos dias de férias tenho direito?</li>
            <li>O que é aviso prévio?</li>
            <li>Quais direitos tem a gestante?</li>
            <li>Qual a jornada máxima diária?</li>
            <li>Posso ser demitido em licença médica?</li>
            <li>Como funciona o FGTS?</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
        <b>🔧 Stack tecnológica</b>
        <ul>
            <li><b>LLM:</b> Gemini 2.5 Flash</li>
            <li><b>Embeddings:</b> text-embedding-004</li>
            <li><b>Vectorstore:</b> ChromaDB</li>
            <li><b>Framework:</b> LangChain + LangGraph</li>
            <li><b>Fonte:</b> CLT · Decreto-Lei 5.452/43</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        "<div style='font-size:0.72rem; color:#7a6e5e; text-align:center; padding-top:0.4rem;'>"
        "Projeto acadêmico · Data Science</div>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.title("⚖️ Assistente da CLT")
st.caption("Tire suas dúvidas sobre a Consolidação das Leis do Trabalho brasileira.")
if agentic_mode:
    st.markdown(
        '<span class="mode-badge">✦ RAG agêntico · avaliação de relevância · LangGraph</span>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<span class="mode-badge-simple">◦ RAG simples · 1 chamada por pergunta</span>',
        unsafe_allow_html=True,
    )

# ── Estado da sessão ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Boas-vindas quando histórico está vazio ───────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <div class="icon">📚</div>
        Faça uma pergunta sobre seus <b>direitos trabalhistas</b>.<br>
        As respostas são baseadas na CLT com citação dos artigos.
    </div>
    """, unsafe_allow_html=True)

# ── Renderiza histórico ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            sources = msg.get("sources", [])
            st.markdown(_inject_tooltips(msg["content"], sources), unsafe_allow_html=True)
            if show_sources and sources:
                _render_sources_expander(sources)
        else:
            st.markdown(msg["content"])

# ── Input e processamento ─────────────────────────────────────────────────────
if question := st.chat_input("Faça sua pergunta sobre a CLT..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Converte histórico para lista de tuplas (humano, assistente)
    msgs = st.session_state.messages[:-1]  # exclui a pergunta atual
    history: list[tuple[str, str]] = []
    for i in range(0, len(msgs) - 1, 2):
        if msgs[i]["role"] == "user" and msgs[i + 1]["role"] == "assistant":
            history.append((msgs[i]["content"], msgs[i + 1]["content"]))

    with st.chat_message("assistant"):
        spinner_text = (
            "Consultando a CLT (modo agêntico)..." if agentic_mode
            else "Consultando a CLT..."
        )
        sources: list[dict] = []
        with st.spinner(spinner_text):
            try:
                if agentic_mode:
                    answer, sources = get_agent_answer_with_sources(question, history)
                else:
                    answer, sources = get_answer_with_sources(question, history)
            except Exception as e:
                answer = (
                    "⚠️ Ocorreu um erro ao processar sua pergunta.\n\n"
                    f"> `{e}`\n\n"
                    "Verifique se o ChromaDB foi gerado e se `GOOGLE_API_KEY` "
                    "está configurada no `.env`."
                )

        st.markdown(_inject_tooltips(answer, sources), unsafe_allow_html=True)
        if show_sources and sources:
            _render_sources_expander(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
