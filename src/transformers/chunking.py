from __future__ import annotations

from typing import Iterator


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 120) -> Iterator[str]:
    text = text.strip()
    if not text:
        return
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        yield text[start:end]
        if end == len(text):
            break
        start = max(0, end - overlap)
