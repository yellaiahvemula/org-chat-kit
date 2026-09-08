"""Ingest org documents."""

from __future__ import annotations

import argparse

from rag.chunker import chunk_markdown
from shared.config import get_documents_dir, get_org_config_dir
from shared.vector_store import store_chunks


def ingest_org(org_id: str, clear_existing: bool = True) -> int:
    docs_dir = get_documents_dir(org_id)
    all_chunks = []
    for path in sorted(docs_dir.glob("**/*")):
        if path.suffix.lower() not in (".md", ".txt"):
            continue
        all_chunks.extend(chunk_markdown(path.read_text(encoding="utf-8"), path.name))
    if not all_chunks:
        return 0
    count = store_chunks(org_id, all_chunks, clear_existing)
    print(f"Ingested {count} chunks for {org_id}")
    return count


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--org", required=True)
    p.add_argument("--no-clear", action="store_true")
    args = p.parse_args()
    get_org_config_dir(args.org)
    ingest_org(args.org, clear_existing=not args.no_clear)


if __name__ == "__main__":
    main()
