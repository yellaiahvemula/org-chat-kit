#!/bin/bash
set -euo pipefail

if ! command -v ollama &>/dev/null; then
  echo "Ollama is not installed"
  exit 1
fi

if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "Ollama is not running"
  exit 0
fi

if command -v brew &>/dev/null && brew services list 2>/dev/null | grep -qE '^ollama[[:space:]]+started'; then
  brew services stop ollama
  echo "Ollama stopped (brew service)"
  exit 0
fi

pkill -f 'ollama serve' 2>/dev/null || pkill -x ollama 2>/dev/null || true

if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "Failed to stop Ollama" >&2
  exit 1
fi

echo "Ollama stopped"
