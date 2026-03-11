from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterable

import requests
from bs4 import BeautifulSoup

from src.utils.retries import request_with_retry

logger = logging.getLogger(__name__)

SITEMAP_URL = "https://help.blip.ai/hc/sitemap.xml"


@dataclass
class CrawledArticle:
    article_id: str
    title: str
    url: str
    locale: str | None
    category: str | None
    section: str | None
    updated_at: str | None
    html: str


def _extract_article_id(url: str) -> str:
    match = re.search(r"/articles/(\d+)", url)
    if match:
        return match.group(1)
    return re.sub(r"[^a-zA-Z0-9]+", "-", url).strip("-")


def _extract_locale(url: str) -> str | None:
    match = re.search(r"/hc/([a-z]{2}-[a-z]{2})/", url.lower())
    return match.group(1) if match else None


class SitemapCrawler:
    def __init__(self, timeout_seconds: int = 10, max_retries: int = 3) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.session = requests.Session()

    def _get(self, url: str) -> requests.Response:
        return request_with_retry(
            session=self.session,
            url=url,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
        )

    def discover_article_urls(self, locale: str | None = None) -> list[str]:
        logger.info("Downloading sitemap: %s", SITEMAP_URL)
        response = self._get(SITEMAP_URL)
        root = ET.fromstring(response.text)

        urls: list[str] = []
        for loc in root.findall(".//{*}loc"):
            value = (loc.text or "").strip()
            if "/articles/" not in value:
                continue
            if locale and f"/hc/{locale.lower()}/" not in value.lower():
                continue
            urls.append(value)

        deduped = sorted(set(urls))
        logger.info("Found URLs in sitemap: %s (deduped: %s)", len(urls), len(deduped))
        return deduped

    def fetch_article(self, url: str) -> CrawledArticle:
        logger.info("Downloading article: %s", url)
        response = self._get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.select_one("h1.article-title") or soup.select_one("h1") or soup.title
        title = title_tag.get_text(" ", strip=True) if title_tag else url

        updated_tag = soup.select_one("time")
        updated_at = updated_tag.get("datetime") if updated_tag else None

        breadcrumbs = soup.select("ol.breadcrumbs li")
        category = breadcrumbs[-3].get_text(" ", strip=True) if len(breadcrumbs) >= 3 else None
        section = breadcrumbs[-2].get_text(" ", strip=True) if len(breadcrumbs) >= 2 else None

        content = soup.select_one("article") or soup.select_one("main") or soup.body
        html = str(content) if content else ""

        return CrawledArticle(
            article_id=_extract_article_id(url),
            title=title,
            url=url,
            locale=_extract_locale(url),
            category=category,
            section=section,
            updated_at=updated_at,
            html=html,
        )

    def iter_articles(self, urls: Iterable[str]) -> Iterable[CrawledArticle]:
        for url in urls:
            try:
                yield self.fetch_article(url)
            except requests.RequestException as exc:
                logger.warning("Failed to download article %s: %s", url, exc)
