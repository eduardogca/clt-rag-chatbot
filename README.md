# ⚖️ CLT RAG Chatbot

Chatbot especialista na Consolidação das Leis do Trabalho (CLT) brasileira, desenvolvido com RAG (Retrieval-Augmented Generation) usando Gemini 1.5 Flash e ChromaDB.

Projeto acadêmico — NLP, 6º Semestre Data Science.

---

## Arquitetura

```
PDF da CLT → Extração → Chunking → Embeddings → ChromaDB
                                                     ↓
                                   Pergunta → Retrieval → Gemini → Resposta
```

## Stack

| Componente | Tecnologia |
|---|---|
| LLM | Gemini 1.5 Flash (Google AI Studio) |
| Embeddings | models/text-embedding-004 (Google) |
| Vectorstore | ChromaDB (persistido no repo) |
| Framework | LangChain |
| Interface | Streamlit |

---

## Estrutura

```
clt-rag-chatbot/
├── data/
│   ├── raw/              # PDF original da CLT
│   ├── processed/        # Texto extraído
│   └── vectorstore/      # ChromaDB persistido
├── src/
│   ├── ingestion/        # Extração, chunking e embeddings (Pessoa 1)
│   ├── retrieval/        # RAG pipeline e LLM (Pessoa 2)
│   └── app/              # Interface Streamlit (Pessoa 3)
├── notebooks/            # Experimentos e avaliação
└── tests/                # Benchmark de perguntas
```

---

## Setup

### 1. Clonar o repositório

```bash
git clone https://github.com/<seu-usuario>/clt-rag-chatbot.git
cd clt-rag-chatbot
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar a API Key

```bash
cp .env.example .env
# Edite o .env e insira sua GOOGLE_API_KEY
```

### 4. Adicionar o PDF da CLT

Coloque o arquivo `clt.pdf` em `data/raw/clt.pdf`.
Download: [Planalto.gov.br](https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm)

### 5. Rodar o pipeline de ingestão (apenas uma vez)

```bash
cd src/ingestion
python extractor.py   # extrai texto do PDF
python embedder.py    # gera embeddings e salva no ChromaDB
```

### 6. Rodar a interface

```bash
streamlit run src/app/streamlit_app.py
```

---

## Divisão de Tarefas

| Pessoa | Responsabilidade | Módulo |
|---|---|---|
| Felipe Teodoro | Extração, chunking e embeddings | `src/ingestion/` |
| Pessoa 2 | RAG pipeline, prompts e avaliação | `src/retrieval/` |
| Pessoa 3 | Interface Streamlit e deploy | `src/app/` |

---

## Exemplos de Perguntas

- "Quantos dias de férias o trabalhador tem direito?"
- "O empregador pode demitir durante licença médica?"
- "Qual a jornada máxima de trabalho diária?"
- "Quais são os direitos da trabalhadora gestante?"
