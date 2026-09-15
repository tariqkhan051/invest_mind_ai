"""HTTP client with retry for data collectors."""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.exceptions import DataProviderUnavailable

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.mufap.com.pk/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1",
}


class CollectorHttpClient:
    """HTTPX wrapper with timeout and retry support."""

    def __init__(
        self,
        timeout_seconds: int = 30,
        retry_attempts: int = 3,
        client: httpx.Client | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._retry_attempts = retry_attempts
        request_headers = {**BROWSER_HEADERS, **(headers or {})}
        self._client = client or httpx.Client(
            timeout=timeout_seconds,
            headers=request_headers,
            follow_redirects=True,
        )
        self._owns_client = client is None

    def close(self) -> None:
        """Close the underlying HTTP client if owned."""
        if self._owns_client:
            self._client.close()

    def get_json(self, url: str) -> Any:
        """Fetch JSON from a URL with retries."""
        return self._request_json("GET", url)

    def get_text(self, url: str) -> str:
        """Fetch raw text from a URL with retries."""
        return self._request_text("GET", url)

    def health_check(self, url: str) -> bool:
        """Return True when the endpoint responds successfully."""
        try:
            response = self._client.get(url, timeout=self._timeout_seconds)
            return response.status_code < 500
        except httpx.HTTPError:
            return False

    def _request_json(self, method: str, url: str) -> Any:
        @retry(
            stop=stop_after_attempt(self._retry_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=15),
            reraise=True,
        )
        def _execute() -> Any:
            try:
                response = self._client.request(
                    method, url, timeout=self._timeout_seconds
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                raise DataProviderUnavailable(
                    f"HTTP request failed for {url}: {exc}"
                ) from exc

        return _execute()

    def _request_text(self, method: str, url: str) -> str:
        @retry(
            stop=stop_after_attempt(self._retry_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=15),
            reraise=True,
        )
        def _execute() -> str:
            try:
                response = self._client.request(
                    method, url, timeout=self._timeout_seconds
                )
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as exc:
                raise DataProviderUnavailable(
                    f"HTTP request failed for {url}: {exc}"
                ) from exc

        return _execute()
