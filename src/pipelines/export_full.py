from __future__ import annotations

import logging
import time
from pathlib import Path

from src.clients.crawler import SitemapCrawler
from src.transformers.chunking import chunk_text
from src.transformers.markdown import article_to_markdown
from src.transformers.normalize import normalize_article
from src.utils.files import ensure_dirs, write_csv, write_json, write_jsonl, write_text

logger = logging.getLogger(__name__)


def run_full_export(output_root: Path, locale: str | None = None) -> dict:
    started = time.perf_counter()
    crawler = SitemapCrawler(timeout_seconds=10, max_retries=3)

    raw_dir = output_root / "raw"
    normalized_dir = output_root / "normalized"
    markdown_dir = output_root / "markdown"
    exports_dir = output_root / "exports"
    ensure_dirs([raw_dir, normalized_dir, markdown_dir, exports_dir])

    urls = crawler.discover_article_urls(locale=locale)
    logger.info("Found URLs: %s", len(urls))

    normalized_rows: list[dict] = []
    chunks_rows: list[dict] = []
    errors = 0

    for article in crawler.iter_articles(urls):
        logger.info("Cleaning HTML: %s", article.url)
        write_text(raw_dir / f"{article.article_id}.html", article.html)

        try:
            normalized = normalize_article(article.__dict__)
        except Exception as exc:
            errors += 1
            logger.warning("Normalize failed for %s: %s", article.url, exc)
            continue

        normalized_dict = normalized.to_dict()
        normalized_rows.append(normalized_dict)
        write_json(normalized_dir / f"{normalized.article_id}.json", normalized_dict)

        logger.info("Generating markdown: %s", article.url)
        markdown = article_to_markdown(normalized.title, normalized.url, article.html)
        write_text(markdown_dir / f"{normalized.article_id}.md", markdown)

        for idx, chunk in enumerate(chunk_text(normalized.content, chunk_size=800)):
            chunks_rows.append(
                {
                    "article_id": normalized.article_id,
                    "chunk_id": f"{normalized.article_id}_{idx}",
                    "title": normalized.title,
                    "url": normalized.url,
                    "content": chunk,
                }
            )

    logger.info("Generating dataset")
    write_jsonl(exports_dir / "articles.jsonl", normalized_rows)
    write_csv(
        exports_dir / "articles.csv",
        normalized_rows,
        fieldnames=["article_id", "title", "url", "locale", "category", "section", "updated_at", "content"],
    )

    logger.info("Generating chunks")
    write_jsonl(exports_dir / "chunks.jsonl", chunks_rows)

    manifest = {
        "source": "sitemap",
        "found": len(urls),
        "deduped": len(urls),
        "success": len(normalized_rows),
        "errors": errors,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "chunks": len(chunks_rows),
    }
    write_json(exports_dir / "manifest.json", manifest)
    write_json(output_root / "manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    import argparse

    from src.utils.logging import configure_logging

    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", default="pt-br")
    parser.add_argument("--output-root", default="data")
    args = parser.parse_args()

    result = run_full_export(Path(args.output_root), locale=args.locale)
    logger.info("Full export complete: %s", result)
