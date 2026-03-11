from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class NormalizedArticle(BaseModel):
    article_id: str = Field(..., min_length=1)
    title: str
    locale: str | None = None
    section_id: int | None = None
    category_id: int | None = None
    author_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    body_html: str
    body_text: str
    source_url: HttpUrl | str
    is_draft: bool | None = None


def normalize_article(raw: dict[str, Any]) -> NormalizedArticle:
    article_id = str(raw.get("id") or raw.get("article_id") or raw.get("url"))
    body_html = raw.get("body") or raw.get("html_body") or ""
    body_text = raw.get("text_body") or raw.get("plain_body") or ""

    return NormalizedArticle(
        article_id=article_id,
        title=raw.get("title", ""),
        locale=raw.get("locale"),
        section_id=raw.get("section_id"),
        category_id=raw.get("category_id"),
        author_id=raw.get("author_id"),
        created_at=raw.get("created_at"),
        updated_at=raw.get("updated_at"),
        body_html=body_html,
        body_text=body_text,
        source_url=raw.get("url", ""),
        is_draft=raw.get("draft") if "draft" in raw else None,
    )
