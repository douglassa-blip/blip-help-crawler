from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime
from pathlib import Path

from src.clients.crawler import HelpCrawler
from src.clients.zendesk import ZendeskClient, ZendeskCredentials
from src.pipelines.export_full import run_full_export
from src.pipelines.export_incremental import run_incremental_export
from src.utils.logging import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export BLiP Help Center data")
    parser.add_argument("--mode", choices=["full", "incremental"], default="full")
    parser.add_argument("--source", choices=["api", "crawler", "auto"], default="auto")
    parser.add_argument("--locale", default=None)
    parser.add_argument("--updated-since", default=None, help="ISO datetime for incremental mode")
    parser.add_argument("--output-root", default=os.getenv("OUTPUT_ROOT", "data"))
    return parser.parse_args()


def collect_from_api(locale: str | None):
    credentials = ZendeskCredentials(
        subdomain=os.environ["ZENDESK_SUBDOMAIN"],
        email=os.environ["ZENDESK_EMAIL"],
        api_token=os.environ["ZENDESK_API_TOKEN"],
    )
    client = ZendeskClient(credentials)
    return list(client.iter_articles(locale=locale))


def collect_from_crawler(locale: str | None):
    crawler = HelpCrawler()
    return list(crawler.iter_pages(locale=locale))


def main() -> None:
    configure_logging()
    args = parse_args()
    logger = logging.getLogger("pipeline")

    source_used = args.source
    articles = []

    if args.source in {"api", "auto"}:
        try:
            articles = collect_from_api(args.locale)
            source_used = "api"
        except Exception as exc:
            if args.source == "api":
                raise
            logger.warning("API collection failed, falling back to crawler: %s", exc)

    if not articles and args.source in {"crawler", "auto"}:
        articles = collect_from_crawler(args.locale)
        source_used = "crawler"

    output_root = Path(args.output_root)

    if args.mode == "incremental":
        if not args.updated_since:
            raise ValueError("--updated-since is required for incremental mode")
        updated_since = datetime.fromisoformat(args.updated_since.replace("Z", "+00:00"))
        manifest = run_incremental_export(articles, output_root=output_root, source_used=source_used, updated_since=updated_since)
    else:
        manifest = run_full_export(articles, output_root=output_root, source_used=source_used)

    logger.info("Export complete: %s", manifest)


if __name__ == "__main__":
    main()
