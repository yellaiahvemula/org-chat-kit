# Org Chat Kit (Python)

A **Python-only** learning and delivery kit for building org-specific conversational AI — for government departments and MSMEs. Includes RAG, agents, FastAPI, Streamlit, and local LLM support via Ollama.

## Stack (100% Python)

| Layer | Tool |
|-------|------|
| RAG | `python/rag/` — ingest, query, citations |
| Agent | `python/agent/` — tools, guardrails, ReAct loop |
| API | **FastAPI** — `app/api.py` |
| UI | **Streamlit** — `app/streamlit_ui.py` |
| Local LLM | **Ollama** — no API key needed |
| Vector store | pgvector or local JSON |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Local LLM (recommended for learning)
cp .env.ollama.example .env
chmod +x scripts/setup-ollama.sh && ./scripts/setup-ollama.sh

# 3. Ingest documents
export PYTHONPATH=python
python -m rag.ingest --org msme-demo

# 4. CLI query
python -m rag.query --org msme-demo "What is UDYAM registration?"
python -m agent.run --org msme-demo "What is PMEGP?"

# 5. Streamlit chat UI
python run_ui.py

# 6. FastAPI (optional)
python run_api.py
# → http://localhost:8000/docs
```

## Project Structure

```
python/
  shared/     config, LLM client, embeddings, vector store
  rag/        chunking, ingest, query
  agent/      tools, ReAct agent
app/
  api.py          FastAPI server
  streamlit_ui.py Chat UI
org-config/
  msme-demo/      branding, prompts, documents, eval set
scripts/          deploy, ollama setup, DB init
```

## Learning Path

1. **Python basics** — run the CLI commands above
2. **RAG** — read `python/rag/`, try ingest + query
3. **Agents** — read `python/agent/tools.py`, test tool calls
4. **Local LLM** — Ollama setup, `python -m shared.llm` to verify
5. **FastAPI** — expose agent as REST API
6. **Streamlit** — chat UI in ~60 lines of Python

## Demo Accounts (API)

- Officer: `officer@msme-demo.gov.in` / `officer123`
- User: `user@example.com` / `user123`

## Cloud vs Local

| | OpenAI | Ollama |
|--|--------|--------|
| Config | `LLM_PROVIDER=openai` | `LLM_PROVIDER=ollama` |
| Key | `OPENAI_API_KEY` | Not needed |
| Re-ingest on switch? | Yes | Yes |

## License

MIT
