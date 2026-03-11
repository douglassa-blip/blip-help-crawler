from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from bs4 import BeautifulSoup


@dataclass
class NormalizedArticle:
    article_id: str
    title: str
    url: str
    locale: str | None
    category: str | None
    section: str | None
    updated_at: str | None
    content: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")

    for selector in [
        "nav",
        "aside",
        "footer",
        "script",
        "style",
        ".breadcrumbs",
        "ol.breadcrumbs",
        ".sidebar",
        "[role='navigation']",
    ]:
        for node in soup.select(selector):
            node.decompose()

    return str(soup)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    return soup.get_text("\n", strip=True)


def normalize_article(raw: dict[str, Any]) -> NormalizedArticle:
    cleaned_html = clean_html(raw.get("html", ""))
    return NormalizedArticle(
        article_id=str(raw.get("article_id", "")),
        title=raw.get("title", ""),
        url=raw.get("url", ""),
        locale=raw.get("locale"),
        category=raw.get("category"),
        section=raw.get("section"),
        updated_at=raw.get("updated_at"),
        content=html_to_text(cleaned_html),
    )
