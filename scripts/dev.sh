#!/bin/bash
# One-command local demo: start Ollama → ingest → FastAPI + Nx React UI
# Usage: ./scripts/dev.sh [org-id]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ORG_ID="${1:-household}"
cd "$ROOT"

# Prefer project venv if present
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/.venv/bin/activate"
fi

export PYTHONPATH="$ROOT/python"

echo "==> Starting Ollama"
"$ROOT/scripts/start-ollama.sh"

CHAT_MODEL="${OLLAMA_MODEL:-llama3.2}"
EMBED_MODEL="${OLLAMA_EMBEDDING_MODEL:-nomic-embed-text}"
if ! curl -sf http://localhost:11434/api/tags | grep -q "$CHAT_MODEL"; then
  echo "==> Pulling chat model: $CHAT_MODEL"
  ollama pull "$CHAT_MODEL"
fi
if ! curl -sf http://localhost:11434/api/tags | grep -q "$EMBED_MODEL"; then
  echo "==> Pulling embedding model: $EMBED_MODEL"
  ollama pull "$EMBED_MODEL"
fi

if [[ ! -f "$ROOT/.env" ]]; then
  echo "==> Creating .env from .env.ollama.example"
  cp "$ROOT/.env.ollama.example" "$ROOT/.env"
fi

if [[ ! -d "$ROOT/node_modules" ]]; then
  echo "==> Installing Nx/React dependencies"
  npm install
fi

echo "==> Ingesting documents for $ORG_ID"
python -m rag.ingest --org "$ORG_ID"

API_PORT="${API_PORT:-8000}"
echo "==> Starting FastAPI on http://localhost:${API_PORT}"
python "$ROOT/run_api.py" &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Wait for API
for _ in $(seq 1 30); do
  if curl -sf "http://localhost:${API_PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

echo "==> Starting Nx React UI on http://localhost:4200"
echo "    API: http://localhost:${API_PORT}/docs"
echo "    Ctrl+C stops API + UI (Ollama keeps running)"
npx nx serve web --host=localhost --port=4200
