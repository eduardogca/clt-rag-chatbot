import sys
import streamlit as st

sys.path.append("src/retrieval")
from chain import build_chain

st.set_page_config(page_title="Assistente CLT", page_icon="⚖️", layout="centered")
st.title("⚖️ Assistente da CLT")
st.caption("Tire suas dúvidas sobre a Consolidação das Leis do Trabalho brasileira.")

if "chain" not in st.session_state:
    with st.spinner("Carregando base de dados da CLT..."):
        st.session_state.chain = build_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Faça sua pergunta sobre a CLT..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando a CLT..."):
            answer = st.session_state.chain.invoke({"query": question})["result"]
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
