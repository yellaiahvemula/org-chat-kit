# Org Chat Kit (Python)

A learning and delivery kit for org-specific conversational AI — RAG, agents, FastAPI, Nx React UI, and local LLM support via Ollama.

## Stack

| Layer | Tool |
|-------|------|
| RAG | `packages/chat-core/rag/` — ingest, query, citations |
| Agent | `packages/chat-core/agent/` — tools, guardrails, ReAct loop |
| API | **FastAPI** — `apps/chat-api/` |
| UI | **Nx React** — `apps/chat-webapp/` (Streamlit still available) |
| Local LLM | **Ollama** — no API key needed |
| Vector store | pgvector or local JSON |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
npm install

# 2. Local LLM (recommended for learning)
cp .env.ollama.example .env
chmod +x scripts/setup-ollama.sh && ./scripts/setup-ollama.sh
./scripts/start-ollama.sh   # start background service
./scripts/stop-ollama.sh    # stop when not needed

# 3. Ingest documents
export PYTHONPATH=packages/chat-core
python -m rag.ingest --org msme-demo

# 4. CLI query
python -m rag.query --org msme-demo "What is UDYAM registration?"
python -m agent.run --org msme-demo "What is PMEGP?"

# 5. One command: Ollama + API + React UI
make start ORG=household
# → http://localhost:4200  (React)
# → http://localhost:8000/docs  (API)
```

## Project Structure

```
apps/
  chat-webapp/          Nx React chat UI
  chat-api/             FastAPI + legacy Streamlit
libs/
  chat-api-client/      Typed HTTP client for the API
  chat-ui/              Shared React chat/expense components
packages/
  chat-core/            Agent, RAG, shared LLM/embeddings, household helpers
org-config/             Per-org branding, prompts, documents
scripts/                Ollama, deploy, DB init
```

## Vision & Core Idea

Personal project direction: **AI Agent + MCP framework that integrates via department APIs (not databases).**

Read the full analysis and roadmap: **[docs/VISION.md](docs/VISION.md)**

OpenAPI-to-MCP connector project: **[docs/OPENAPI-MCP-WRAPPER.md](docs/OPENAPI-MCP-WRAPPER.md)** → [openapi-mcp-wrapper](https://github.com/yellaiahvemula/openapi-mcp-wrapper)

## Learning Path

**New to Python, Ollama, RAG, FastAPI?** Start here:

**[docs/LEARNING.md](docs/LEARNING.md)** — ordered guide from Python basics → Ollama → RAG → Agents → FastAPI → MCP/connectors.

Quick reference once you're set up:

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
