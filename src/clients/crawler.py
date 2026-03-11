from __future__ import annotations

import logging
from collections import deque
from typing import Iterator, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.utils.retries import with_http_retry

logger = logging.getLogger(__name__)


class HelpCrawler:
    def __init__(self, base_url: str = "https://help.blip.ai", timeout_seconds: int = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    @with_http_retry()
    def _get(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.text

    def iter_pages(self, locale: Optional[str] = None, max_pages: int = 500) -> Iterator[dict]:
        start_url = self.base_url
        if locale:
            start_url = f"{start_url}/hc/{locale}"

        visited: set[str] = set()
        queue: deque[str] = deque([start_url])

        while queue and len(visited) < max_pages:
            url = queue.popleft()
            if url in visited:
                continue

            visited.add(url)
            try:
                html = self._get(url)
            except requests.RequestException as exc:
                logger.warning("Failed to crawl %s: %s", url, exc)
                continue

            soup = BeautifulSoup(html, "html.parser")
            main_content = soup.find("main") or soup.find("article") or soup.body
            text_content = main_content.get_text("\n", strip=True) if main_content else ""
            title = soup.title.string.strip() if soup.title and soup.title.string else url

            yield {
                "id": f"crawler::{url}",
                "title": title,
                "url": url,
                "html_body": str(main_content) if main_content else "",
                "text_body": text_content,
            }

            for anchor in soup.find_all("a", href=True):
                next_url = urljoin(url, anchor["href"])
                parsed = urlparse(next_url)
                if parsed.scheme not in {"http", "https"}:
                    continue
                if parsed.netloc != urlparse(self.base_url).netloc:
                    continue
                clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
                if clean and clean not in visited:
                    queue.append(clean)
