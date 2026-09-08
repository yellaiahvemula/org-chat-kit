"""ReAct agent."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from agent.tools import execute_tool, get_enabled_tools, redact_pii
from shared.config import load_system_prompt, load_tools_config
from shared.llm import chat_completion, is_llm_available


@dataclass
class AgentResult:
    answer: str
    tools_called: list[dict] = field(default_factory=list)
    confidence: float = 0.0
    escalated: bool = False


def run_agent_mock(org_id: str, query: str) -> AgentResult:
    m = re.search(r"UDYAM-[A-Z]{2}-\d{2}-\d{7}", query, re.I)
    if m or "udyam status" in query.lower():
        r = execute_tool(org_id, "get_business_registration_status", {"registration_number": m.group(0) if m else "UDYAM-MH-01-0001234"})
        if r.get("found"):
            return AgentResult(
                answer=f"**{r['registration_number']}** — {r['business_name']} is **{r['status']}** ({r['category']}, {r['state']})",
                tools_called=[{"tool": "get_business_registration_status", "result": r}], confidence=1.0)
    if any(w in query.lower() for w in ("ticket", "support", "officer")):
        r = execute_tool(org_id, "create_support_ticket", {"subject": "Support request", "description": query})
        return AgentResult(answer=r["message"], tools_called=[{"tool": "create_support_ticket", "result": r}], confidence=1.0)
    rag = execute_tool(org_id, "search_knowledge_base", {"query": query})
    min_c = load_tools_config(org_id).get("retrieval", {}).get("min_confidence", 0.65)
    if not is_llm_available():
        min_c = min(min_c, 0.30)
    if rag["confidence"] < min_c:
        return AgentResult(answer="I don't have enough information. Create a support ticket?", confidence=rag["confidence"], escalated=True,
                           tools_called=[{"tool": "search_knowledge_base"}])
    ans = rag["answer"] + (f"\n\n**Sources:**\n{rag['citations']}" if rag.get("citations") else "")
    return AgentResult(answer=ans, tools_called=[{"tool": "search_knowledge_base"}], confidence=rag["confidence"])


def run_agent(org_id: str, query: str, max_iter: int = 5) -> AgentResult:
    if not is_llm_available():
        return run_agent_mock(org_id, query)

    tools = get_enabled_tools(org_id)
    otools = [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}} for t in tools]
    messages = [{"role": "system", "content": load_system_prompt(org_id)}, {"role": "user", "content": redact_pii(query)}]
    called, confidence = [], 0.0

    for _ in range(max_iter):
        resp = chat_completion(messages=messages, tools=otools or None, temperature=0.2)
        ch = resp.choices[0]
        if ch.finish_reason == "tool_calls" and ch.message.tool_calls:
            messages.append(ch.message)
            for tc in ch.message.tool_calls:
                args = json.loads(tc.function.arguments)
                result = execute_tool(org_id, tc.function.name, args)
                called.append({"tool": tc.function.name, "arguments": args, "result": result})
                if tc.function.name == "search_knowledge_base":
                    confidence = result.get("confidence", 0)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
            continue
        return AgentResult(answer=ch.message.content or "", tools_called=called, confidence=confidence)

    return AgentResult(answer="Unable to complete request.", tools_called=called, escalated=True)
