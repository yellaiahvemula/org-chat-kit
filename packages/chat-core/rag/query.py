"""RAG query with citations."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass

from shared.config import load_system_prompt, load_tools_config
from shared.llm import chat_completion, is_llm_available
from shared.vector_store import search_chunks


@dataclass
class RetrievedChunk:
    content: str
    document_name: str
    section: str | None
    similarity: float


def retrieve(org_id: str, query: str, top_k: int = 5) -> list[RetrievedChunk]:
    rows = search_chunks(org_id, query, top_k)
    return [RetrievedChunk(r["content"], r["document_name"], r.get("section"), float(r["similarity"])) for r in rows]


def hybrid_retrieve(org_id: str, query: str, top_k: int = 5) -> list[RetrievedChunk]:
    results = retrieve(org_id, query, top_k * 2)
    terms = set(re.findall(r"\w+", query.lower()))
    scored = []
    for c in results:
        boost = sum(1 for t in terms if t in c.content.lower()) / max(len(terms), 1) * 0.2
        scored.append((c, c.similarity + boost))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in scored[:top_k]]


def format_citations(chunks: list[RetrievedChunk]) -> str:
    return "\n".join(
        f"[{i}] {c.document_name}" + (f" — {c.section}" if c.section else "") + f" ({c.similarity:.2f})"
        for i, c in enumerate(chunks, 1)
    )


def _mock_answer(chunks: list[RetrievedChunk]) -> str:
    if not chunks or chunks[0].similarity < 0.3:
        return "I don't have enough information. Would you like to create a support ticket?"
    c = chunks[0]
    sec = f" ({c.section})" if c.section else ""
    return f"Based on {c.document_name}{sec}:\n\n{c.content[:600]}\n\nSources:\n{format_citations(chunks)}"


def query_rag(org_id: str, question: str) -> dict:
    cfg = load_tools_config(org_id)
    rc = cfg.get("retrieval", {})
    top_k = rc.get("top_k", 5)
    min_conf = rc.get("min_confidence", 0.65)
    if not is_llm_available():
        min_conf = min(min_conf, 0.30)

    chunks = hybrid_retrieve(org_id, question, top_k) if rc.get("hybrid_search", True) else retrieve(org_id, question, top_k)
    avg = sum(c.similarity for c in chunks) / len(chunks) if chunks else 0
    conf = max(avg, max((c.similarity for c in chunks), default=0) * 0.8)

    if conf < min_conf or not chunks:
        return {"answer": "I don't have enough information. Would you like to create a support ticket?",
                "citations": format_citations(chunks), "chunks": [], "confidence": conf}

    ctx = "\n\n---\n\n".join(f"Source: {c.document_name}\n{c.content}" for c in chunks)
    if is_llm_available():
        resp = chat_completion([
            {"role": "system", "content": load_system_prompt(org_id)},
            {"role": "user", "content": f"Answer using ONLY this context. Cite sources.\n\n{ctx}\n\nQuestion: {question}"},
        ], temperature=0.2)
        answer = resp.choices[0].message.content or _mock_answer(chunks)
    else:
        answer = _mock_answer(chunks)

    return {"answer": answer, "citations": format_citations(chunks),
            "chunks": [{"document_name": c.document_name, "section": c.section, "similarity": c.similarity,
                        "content_preview": c.content[:200]} for c in chunks], "confidence": conf}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--org", required=True)
    p.add_argument("question", nargs="+")
    args = p.parse_args()
    r = query_rag(args.org, " ".join(args.question))
    print(f"\n{r['answer']}\n\nConfidence: {r['confidence']:.2f}\n\n{r['citations']}")


if __name__ == "__main__":
    main()
