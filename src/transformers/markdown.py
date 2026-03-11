from __future__ import annotations

from markdownify import markdownify


def article_to_markdown(title: str, source_url: str, html_body: str) -> str:
    markdown_body = markdownify(html_body or "", heading_style="ATX")
    return f"# {title}\n\nSource: {source_url}\n\n{markdown_body}\n"
