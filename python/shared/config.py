"""Shared configuration."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
ORG_CONFIG_DIR = ROOT_DIR / "org-config"

load_dotenv(ROOT_DIR / ".env")


def get_org_config_dir(org_id: str) -> Path:
    path = ORG_CONFIG_DIR / org_id
    if not path.exists():
        raise FileNotFoundError(f"Org config not found: {org_id}")
    return path


def load_branding(org_id: str) -> dict[str, Any]:
    with open(get_org_config_dir(org_id) / "branding.yaml") as f:
        return yaml.safe_load(f)


def load_tools_config(org_id: str) -> dict[str, Any]:
    with open(get_org_config_dir(org_id) / "tools.yaml") as f:
        return yaml.safe_load(f)


def load_system_prompt(org_id: str) -> str:
    return (get_org_config_dir(org_id) / "system-prompt.md").read_text()


def load_eval_questions(org_id: str) -> list[dict[str, Any]]:
    path = get_org_config_dir(org_id) / "eval-questions.jsonl"
    return [json.loads(line) for line in path.read_text().strip().split("\n") if line.strip()]


def get_documents_dir(org_id: str) -> Path:
    return get_org_config_dir(org_id) / "documents"


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "postgresql://orgchat:orgchat@localhost:5432/orgchat")


def get_llm_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "openai")


def get_openai_api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY")


def list_orgs() -> list[str]:
    return sorted(p.name for p in ORG_CONFIG_DIR.iterdir() if p.is_dir() and (p / "branding.yaml").exists())


def mock_embedding(text: str, dim: int = 1536) -> list[float]:
    h = hashlib.sha256(text.encode()).digest()
    return [(h[i % len(h)] / 127.5) - 1.0 for i in range(dim)]
