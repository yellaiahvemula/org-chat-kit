"""Vector store: Postgres/pgvector or local JSON."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from shared.config import ROOT_DIR
from shared.embeddings import get_embedding, get_embeddings


LOCAL_STORE = ROOT_DIR / "data" / "vector-store.json"


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def _use_postgres() -> bool:
    try:
        from shared.db import get_connection
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False


def store_chunks(org_id: str, chunks: list, clear_existing: bool = True) -> int:
    texts = [c.content for c in chunks]
    embeddings = get_embeddings(texts)

    if _use_postgres():
        import json as _json
        from psycopg2.extras import execute_values
        from shared.db import get_connection, init_database
        init_database()
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                if clear_existing:
                    cur.execute("DELETE FROM document_chunks WHERE org_id = %s", (org_id,))
                rows = [(org_id, c.document_name, c.section, c.page_number, c.content, emb, _json.dumps(c.metadata or {}))
                        for c, emb in zip(chunks, embeddings)]
                execute_values(cur,
                    "INSERT INTO document_chunks (org_id,document_name,section,page_number,content,embedding,metadata) VALUES %s",
                    rows, template="(%s,%s,%s,%s,%s,%s::vector,%s::jsonb)")
            conn.commit()
            return len(rows)
        finally:
            conn.close()

    store = json.loads(LOCAL_STORE.read_text()) if LOCAL_STORE.exists() else []
    if clear_existing:
        store = [s for s in store if s["org_id"] != org_id]
    for chunk, emb in zip(chunks, embeddings):
        store.append({"org_id": org_id, "document_name": chunk.document_name, "section": chunk.section,
                      "page_number": chunk.page_number, "content": chunk.content, "embedding": emb,
                      "metadata": chunk.metadata or {}})
    LOCAL_STORE.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_STORE.write_text(json.dumps(store))
    return len(chunks)


def search_chunks(org_id: str, query: str, top_k: int = 5) -> list[dict]:
    embedding = get_embedding(query)
    if _use_postgres():
        from shared.db import get_connection, get_dict_cursor, init_database
        init_database()
        emb_str = "[" + ",".join(str(v) for v in embedding) + "]"
        conn = get_connection()
        try:
            with get_dict_cursor(conn) as cur:
                cur.execute(
                    "SELECT content,document_name,section,1-(embedding<=>%s::vector) AS similarity "
                    "FROM document_chunks WHERE org_id=%s ORDER BY embedding<=>%s::vector LIMIT %s",
                    (emb_str, org_id, emb_str, top_k))
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    store = json.loads(LOCAL_STORE.read_text()) if LOCAL_STORE.exists() else []
    store = [s for s in store if s["org_id"] == org_id]
    terms = set(re.findall(r"\w+", query.lower()))
    scored = []
    for s in store:
        cl = s["content"].lower()
        tl = s.get("document_name", "").lower().replace("-", " ").replace(".md", "")
        kh = sum(1 for t in terms if len(t) > 2 and t in cl)
        th = sum(1 for t in terms if len(t) > 2 and t in tl)
        ks = min((kh + th * 2) / max(len(terms), 1), 1.0)
        scored.append({**s, "similarity": 0.7 * ks + 0.3 * max(_cosine(embedding, s["embedding"]), 0)})
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]
