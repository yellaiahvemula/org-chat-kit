"""Unified LLM client for OpenAI and Ollama."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from shared.config import get_llm_provider, get_openai_api_key


def get_ollama_base_url() -> str:
    return os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")


def ollama_is_running() -> bool:
    try:
        return httpx.get(f"{get_ollama_base_url()}/api/tags", timeout=3).status_code == 200
    except Exception:
        return False


def list_ollama_models() -> list[str]:
    try:
        resp = httpx.get(f"{get_ollama_base_url()}/api/tags", timeout=5)
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []


def is_llm_available() -> bool:
    if get_llm_provider() == "openai" and get_openai_api_key():
        return True
    if get_llm_provider() == "ollama":
        return ollama_is_running()
    return False


def get_llm_client():
    provider = get_llm_provider()
    if provider == "ollama" and ollama_is_running():
        from openai import OpenAI
        return OpenAI(
            base_url=f"{get_ollama_base_url()}/v1",
            api_key=os.environ.get("OLLAMA_API_KEY", "ollama"),
        ), os.environ.get("OLLAMA_MODEL", "llama3.2")
    if provider == "openai" and get_openai_api_key():
        from openai import OpenAI
        return OpenAI(api_key=get_openai_api_key()), os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    return None, None


def chat_completion(messages: list[dict[str, Any]], *, temperature: float = 0.2, tools: list | None = None):
    client, model = get_llm_client()
    if not client:
        raise RuntimeError("No LLM available. Set OPENAI_API_KEY or start Ollama.")
    kwargs: dict[str, Any] = {"model": model, "messages": messages, "temperature": temperature}
    if tools:
        kwargs["tools"] = tools
    return client.chat.completions.create(**kwargs)


def check_setup() -> dict:
    provider = get_llm_provider()
    result: dict[str, Any] = {
        "provider": provider,
        "llm_available": is_llm_available(),
        "ollama_running": ollama_is_running(),
        "recommendations": [],
    }
    if provider == "ollama":
        result["ollama_models"] = list_ollama_models()
        result["chat_model"] = os.environ.get("OLLAMA_MODEL", "llama3.2")
        missing = [m for m in [result["chat_model"], os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")]
                   if not any(m in i for i in result["ollama_models"])]
        if missing:
            result["recommendations"].append(f"Pull models: ollama pull {' && ollama pull '.join(missing)}")
        if not result["ollama_running"]:
            result["recommendations"].append("Start Ollama: ollama serve")
    elif not get_openai_api_key():
        result["recommendations"].append("Set OPENAI_API_KEY or switch to LLM_PROVIDER=ollama")
    return result


if __name__ == "__main__":
    print(json.dumps(check_setup(), indent=2))
