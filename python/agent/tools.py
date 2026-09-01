"""Agent tools."""

from __future__ import annotations

import re
import uuid
from typing import Any

from rag.query import query_rag
from shared.config import load_tools_config
from shared.llm import is_llm_available

PII = [re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), re.compile(r"\b\d{10}\b")]

MOCK_UDYAM = {
    "UDYAM-MH-01-0001234": {"business_name": "Sharma Textiles Pvt Ltd", "status": "active", "category": "micro", "state": "Maharashtra"},
    "UDYAM-DL-02-0005678": {"business_name": "Delhi Spice Exports", "status": "active", "category": "small", "state": "Delhi"},
}


def redact_pii(text: str) -> str:
    for p in PII:
        text = p.sub("[REDACTED]", text)
    return text


def search_knowledge_base(org_id: str, query: str) -> dict:
    return query_rag(org_id, query)


def get_business_registration_status(org_id: str, registration_number: str) -> dict:
    data = MOCK_UDYAM.get(registration_number.upper())
    if not data:
        return {"found": False, "message": f"No registration found for {registration_number}"}
    return {"found": True, "registration_number": registration_number.upper(), **data}


def create_support_ticket(org_id: str, subject: str, description: str, user_email: str | None = None) -> dict:
    tid = str(uuid.uuid4())[:8].upper()
    return {"ticket_id": tid, "status": "open",
            "message": "Support ticket created. An officer will follow up within 2 business days.", "subject": subject}


TOOL_DEFINITIONS = [
    {"name": "search_knowledge_base", "description": "Search org knowledge base for schemes and processes",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "get_business_registration_status", "description": "Look up UDYAM registration status",
     "parameters": {"type": "object", "properties": {"registration_number": {"type": "string"}}, "required": ["registration_number"]}},
    {"name": "create_support_ticket", "description": "Create support ticket for officer follow-up",
     "parameters": {"type": "object", "properties": {"subject": {"type": "string"}, "description": {"type": "string"},
                    "user_email": {"type": "string"}}, "required": ["subject", "description"]}},
]


def execute_tool(org_id: str, name: str, args: dict) -> dict:
    if name == "search_knowledge_base":
        return search_knowledge_base(org_id, args["query"])
    if name == "get_business_registration_status":
        return get_business_registration_status(org_id, args["registration_number"])
    if name == "create_support_ticket":
        return create_support_ticket(org_id, args["subject"], args["description"], args.get("user_email"))
    return {"error": f"Unknown tool: {name}"}


def get_enabled_tools(org_id: str) -> list[dict]:
    enabled = set(load_tools_config(org_id).get("enabled_tools", []))
    return [t for t in TOOL_DEFINITIONS if t["name"] in enabled]
