#!/bin/bash
set -euo pipefail

if ! command -v ollama &>/dev/null; then
  echo "Install Ollama from https://ollama.com/download"
  exit 1
fi

wait_for_ollama() {
  local i
  for i in $(seq 1 20); do
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "Ollama is already running at http://localhost:11434"
  exit 0
fi

if command -v brew &>/dev/null && brew list ollama &>/dev/null 2>&1; then
  brew services start ollama
else
  nohup ollama serve >/dev/null 2>&1 &
fi

if wait_for_ollama; then
  echo "Ollama started at http://localhost:11434"
else
  echo "Failed to start Ollama" >&2
  exit 1
fi
