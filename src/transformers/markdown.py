from __future__ import annotations

from markdownify import markdownify as md


def article_to_markdown(title: str, source_url: str, html_body: str) -> str:
    markdown_body = md(html_body or "")
    return f"# {title}\n\nSource: {source_url}\n\n{markdown_body}\n"
