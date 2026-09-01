#!/bin/bash
set -euo pipefail
if ! command -v ollama &>/dev/null; then
  echo "Install Ollama from https://ollama.com/download"
  exit 1
fi
CHAT="${OLLAMA_MODEL:-llama3.2}"
EMBED="${OLLAMA_EMBEDDING_MODEL:-nomic-embed-text}"
curl -sf http://localhost:11434/api/tags >/dev/null || (ollama serve & sleep 3)
ollama pull "$CHAT"
ollama pull "$EMBED"
echo "Done. cp .env.ollama.example .env"
