import streamlit as st
from src.retrieval.chain import get_answer

st.set_page_config(page_title="Assistente CLT", page_icon="⚖️", layout="centered")
st.title("⚖️ Assistente da CLT")
st.caption("Tire suas dúvidas sobre a Consolidação das Leis do Trabalho brasileira.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Faça sua pergunta sobre a CLT..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Converte o histórico de mensagens para lista de tuplas (humano, assistente)
    msgs = st.session_state.messages[:-1]  # exclui a pergunta atual
    history: list[tuple[str, str]] = []
    for i in range(0, len(msgs) - 1, 2):
        if msgs[i]["role"] == "user" and msgs[i + 1]["role"] == "assistant":
            history.append((msgs[i]["content"], msgs[i + 1]["content"]))

    with st.chat_message("assistant"):
        with st.spinner("Consultando a CLT..."):
            answer = get_answer(question, history)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
