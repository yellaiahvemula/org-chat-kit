"""Section-aware markdown chunking."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    document_name: str
    section: str | None = None
    page_number: int | None = None
    metadata: dict | None = None


def chunk_markdown(text: str, document_name: str, max_chars: int = 1500) -> list[Chunk]:
    chunks: list[Chunk] = []
    for section_text in re.split(r"(?=^#{1,3} )", text, flags=re.MULTILINE):
        section_text = section_text.strip()
        if not section_text:
            continue
        title = section_text.split("\n")[0].lstrip("#").strip() if section_text.startswith("#") else None
        if len(section_text) <= max_chars:
            chunks.append(Chunk(section_text, document_name, title))
        else:
            for i in range(0, len(section_text), max_chars):
                chunks.append(Chunk(section_text[i:i + max_chars], document_name, title))
    return chunks
