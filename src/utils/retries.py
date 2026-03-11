from __future__ import annotations

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


@retry(
    retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError, requests.HTTPError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def request_with_retry(
    session: requests.Session,
    url: str,
    timeout_seconds: int = 10,
    max_retries: int = 3,
) -> requests.Response:
    # max_retries is kept in signature for caller clarity/config compatibility.
    response = session.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    return response
