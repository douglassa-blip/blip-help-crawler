from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter
from typing import Iterable

import pandas as pd

from src.transformers.markdown import article_to_markdown
from src.transformers.normalize import NormalizedArticle, normalize_article
from src.utils.files import append_jsonl, ensure_dirs, write_json

logger = logging.getLogger(__name__)


def _dedupe_articles(raw_articles: Iterable[dict]) -> list[dict]:
    unique_by_id: dict[str, dict] = {}
    seen_urls: set[str] = set()

    for article in raw_articles:
        article_id = str(article.get("id") or article.get("article_id") or "")
        canonical_url = (article.get("url") or "").strip().lower()

        if article_id and article_id in unique_by_id:
            continue
        if canonical_url and canonical_url in seen_urls:
            continue

        if article_id:
            unique_by_id[article_id] = article
        elif canonical_url:
            unique_by_id[canonical_url] = article

        if canonical_url:
            seen_urls.add(canonical_url)

    return list(unique_by_id.values())


def run_full_export(raw_articles: Iterable[dict], output_root: Path, source_used: str) -> dict:
    started = perf_counter()
    raw_articles = list(raw_articles)

    raw_dir = output_root / "raw"
    normalized_dir = output_root / "normalized"
    markdown_dir = output_root / "markdown"
    exports_dir = output_root / "exports"
    ensure_dirs([raw_dir, normalized_dir, markdown_dir, exports_dir])

    deduped = _dedupe_articles(raw_articles)
    normalized_articles: list[NormalizedArticle] = []
    errors = 0

    for raw in deduped:
        article_key = str(raw.get("id") or raw.get("url") or "unknown")
        write_json(raw_dir / f"{article_key}.json", raw)
        try:
            normalized = normalize_article(raw)
        except Exception as exc:
            errors += 1
            logger.warning("Normalize failed for %s: %s", article_key, exc)
            continue

        normalized_articles.append(normalized)
        write_json(normalized_dir / f"{normalized.article_id}.json", normalized.model_dump(mode="json"))

        markdown = article_to_markdown(
            title=normalized.title,
            source_url=str(normalized.source_url),
            html_body=normalized.body_html,
        )
        (markdown_dir / f"{normalized.article_id}.md").write_text(markdown, encoding="utf-8")

    as_dicts = [item.model_dump(mode="json") for item in normalized_articles]
    append_jsonl(exports_dir / "articles.jsonl", as_dicts)
    pd.DataFrame(as_dicts).to_csv(exports_dir / "articles.csv", index=False)

    manifest = {
        "source": source_used,
        "found": len(raw_articles),
        "deduped": len(deduped),
        "success": len(normalized_articles),
        "errors": errors,
        "elapsed_seconds": round(perf_counter() - started, 2),
    }
    write_json(exports_dir / "manifest.json", manifest)
    return manifest
