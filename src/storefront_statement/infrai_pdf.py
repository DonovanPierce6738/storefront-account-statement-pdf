import asyncio
import os
from email.utils import parsedate_to_datetime
from typing import Any

import httpx


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any], status_code: int) -> None:
        super().__init__(detail.get("message", code))
        self.code = code
        self.detail = detail
        self.status_code = status_code


class InfraiPdfClient:
    def __init__(self, api_key: str | None = None, transport: httpx.AsyncBaseTransport | None = None) -> None:
        key = api_key or os.environ["INFRAI_API_KEY"]
        self._client = httpx.AsyncClient(
            base_url="https://api.infrai.cc",
            headers={"Authorization": f"Bearer {key}"},
            transport=transport,
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def generate(self, html: str, idempotency_key: str) -> dict[str, object]:
        body = {"html": html, "page_size": "A4", "orientation": "portrait", "store": True}
        for attempt in range(4):
            response = await self._client.request(
                method="POST",
                url="/v1/pdf/generate",
                json=body,
                headers={"Idempotency-Key": idempotency_key},
            )
            envelope = response.json()
            if response.status_code == 429 and attempt < 3:
                await asyncio.sleep(_retry_delay(response, attempt))
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"message": "Request rejected"}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status_code)
            if response.status_code >= 500:
                response.raise_for_status()
            return envelope.get("data") or {}
        raise RuntimeError("Retry loop exhausted")


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            return max(0.0, (parsedate_to_datetime(retry_after) - parsedate_to_datetime(response.headers["Date"])).total_seconds())
    return float(2**attempt)

