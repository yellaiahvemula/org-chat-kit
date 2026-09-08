"""Embeddings: OpenAI, Ollama, or mock."""

from __future__ import annotations

import os

import httpx

from shared.config import get_llm_provider, get_openai_api_key, mock_embedding
from shared.llm import ollama_is_running


def get_embedding_dim() -> int:
    if os.environ.get("EMBEDDING_DIM"):
        return int(os.environ["EMBEDDING_DIM"])
    if get_llm_provider() == "ollama":
        return 768
    if get_llm_provider() == "openai" and get_openai_api_key():
        return 1536
    return 1536


def get_embeddings(texts: list[str]) -> list[list[float]]:
    provider = get_llm_provider()
    if provider == "openai" and get_openai_api_key():
        from openai import OpenAI
        client = OpenAI(api_key=get_openai_api_key())
        model = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        return [e.embedding for e in client.embeddings.create(input=texts, model=model).data]
    if provider == "ollama" and ollama_is_running():
        base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        model = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        out = []
        with httpx.Client(timeout=120) as c:
            for text in texts:
                r = c.post(f"{base}/api/embeddings", json={"model": model, "prompt": text})
                r.raise_for_status()
                out.append(r.json()["embedding"])
        return out
    dim = get_embedding_dim()
    return [mock_embedding(t, dim) for t in texts]


def get_embedding(text: str) -> list[float]:
    return get_embeddings([text])[0]
