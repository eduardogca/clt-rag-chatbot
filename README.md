### 4. Rodar a interface

```bash
# Windows
set PYTHONPATH=. && py -3.11 -m streamlit run src/app/streamlit_app.py

# Linux / Mac
PYTHONPATH=. streamlit run src/app/streamlit_app.py
```

> **Nota:** o ChromaDB já está persistido no repositório em `data/vectorstore/`. Não é necessário rodar o pipeline de ingestão novamente.

---

## Pipeline de Ingestão (referência)

Caso precise regenerar o vectorstore do zero:

```bash
python src/ingestion/extractor.py    # extrai texto do PDF
python src/ingestion/chunker.py      # divide por artigo com metadados
python src/ingestion/embedder.py     # gera embeddings e salva no ChromaDB
```

O chunking foi feito por artigo (1.183 chunks), com metadados de artigo e seção para citação precisa nas respostas.

---

## Pipeline RAG Agêntico

O sistema usa um grafo LangGraph com avaliação de relevância em dois estágios:

1. **Retrieval** — recupera k=8 chunks do ChromaDB
2. **Avaliação** — pontuação combinada: `0.4 × cosine_similarity + 0.6 × llm_judge`
3. **Decisão** — se score médio < 0.45 e tentativas < 3, reformula a query e repete
4. **Geração** — usa apenas chunks com score ≥ 0.45 para gerar a resposta

---

## Divisão de Tarefas

| Pessoa | Responsabilidade | Módulo |
|---|---|---|
| Felipe Teodoro | Data pipeline: extração, chunking e embeddings | `src/ingestion/` + `notebooks/01` |
| Pessoa 2 | RAG core: retrieval, prompts, avaliação e LangGraph | `src/retrieval/` + `notebooks/02` |
| Pessoa 3 | Interface Streamlit, deploy e documentação | `src/app/` + `README` |

---

## Exemplos de Perguntas

- "Quantos dias de férias o trabalhador tem direito por ano?"
- "O empregador pode demitir durante licença médica?"
- "Qual a jornada máxima de trabalho diária?"
- "Quais são os direitos da trabalhadora gestante?"
- "O que é aviso prévio e qual o prazo mínimo?"
- "Como funciona o FGTS?"

---

## Licença

Projeto acadêmico sem fins comerciais. A CLT é documento de domínio público.
