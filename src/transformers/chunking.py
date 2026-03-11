from __future__ import annotations

from typing import Iterable


def chunk_text(text: str, chunk_size: int = 800) -> Iterable[str]:
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        chunks.append(cleaned[start : start + chunk_size])
        start += chunk_size
    return chunks
