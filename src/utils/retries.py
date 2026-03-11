from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import requests


def with_http_retry(attempts: int = 5):
    return retry(
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError, requests.HTTPError)),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        stop=stop_after_attempt(attempts),
        reraise=True,
    )
