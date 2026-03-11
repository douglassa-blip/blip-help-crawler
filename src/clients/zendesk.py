from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional

import requests

from src.utils.retries import with_http_retry

logger = logging.getLogger(__name__)


@dataclass
class ZendeskCredentials:
    subdomain: str
    email: str
    api_token: str


class ZendeskClient:
    def __init__(self, credentials: ZendeskCredentials, timeout_seconds: int = 20) -> None:
        self.base_url = f"https://{credentials.subdomain}.zendesk.com/api/v2/help_center"
        self.session = requests.Session()
        self.session.auth = (f"{credentials.email}/token", credentials.api_token)
        self.timeout_seconds = timeout_seconds

    @with_http_retry()
    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        response = self.session.get(
            f"{self.base_url}{endpoint}", params=params, timeout=self.timeout_seconds
        )
        response.raise_for_status()
        return response.json()

    def iter_articles(self, locale: Optional[str] = None, start_time: Optional[datetime] = None) -> Iterator[dict]:
        endpoint = "/articles.json"
        params: dict = {"per_page": 100}
        if locale:
            params["locale"] = locale
        if start_time:
            params["start_time"] = int(start_time.timestamp())

        while endpoint:
            payload = self._get(endpoint, params=params)
            params = None
            articles = payload.get("articles", [])
            logger.info("Fetched %s articles from endpoint %s", len(articles), endpoint)
            for article in articles:
                yield article

            next_page = payload.get("next_page")
            if not next_page:
                endpoint = ""
                continue

            endpoint = next_page.replace(self.base_url, "")
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint
