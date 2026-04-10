from datetime import date
from types import SimpleNamespace
from typing import Any
import asyncio

import aiohttp
import pytest

from ecb_rate.client import ECBJsonClient
from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import EcbApiError


class FakeResponse:
    def __init__(
        self,
        *,
        status: int = 200,
        reason: str = "OK",
        json_data: Any = None,
        text_data: str = "",
        json_exc: Exception | None = None,
    ) -> None:
        self.status = status
        self.reason = reason
        self._json_data = json_data
        self._text_data = text_data
        self._json_exc = json_exc

    async def json(self) -> Any:
        if self._json_exc is not None:
            raise self._json_exc
        return self._json_data

    async def text(self) -> str:
        return self._text_data

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class FakeSession:
    def __init__(
        self,
        response: FakeResponse | None = None,
        *,
        get_exc: Exception | None = None,
    ) -> None:
        self._response = response
        self._get_exc = get_exc
        self.request_url: str | None = None
        self.request_kwargs: dict[str, Any] | None = None

    def get(self, url: str, **kwargs):
        self.request_url = url
        self.request_kwargs = kwargs

        if self._get_exc is not None:
            raise self._get_exc

        if self._response is None:  # pragma: no cover
            raise AssertionError("FakeSession.get() called without configured response.")

        return self._response

    async def __aenter__(self) -> "FakeSession":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


@pytest.mark.asyncio
async def test_fetch_success_builds_expected_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = FakeResponse(json_data={"dataSets": []})
    fake_session = FakeSession(response)
    captured: dict[str, Any] = {}

    def fake_client_session(*, timeout, headers):
        captured["timeout"] = timeout
        captured["headers"] = headers
        return fake_session

    monkeypatch.setattr("ecb_rate.client.aiohttp.ClientSession", fake_client_session)

    client = ECBJsonClient(timeout_seconds=17)
    result = await client.fetch(CurrencyType.TRY, date(2025, 6, 6))

    assert result == {"dataSets": []}
    assert fake_session.request_url == (
        "https://data-api.ecb.europa.eu/service/data/EXR/D.TRY.EUR.SP00.A"
    )
    assert fake_session.request_kwargs == {
        "params": {
            "format": "jsondata",
            "lastNObservations": 1,
            "endPeriod": "2025-06-06",
            "details": "dataonly",
        }
    }
    assert captured["headers"]["Accept"] == "application/json"
    assert captured["headers"]["User-Agent"] == "ecb_rate/0.1.0"
    assert isinstance(captured["timeout"], aiohttp.ClientTimeout)
    assert captured["timeout"].total == 17


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "reason", "body"),
    [
        (400, "Bad Request", "bad request"),
        (404, "Not Found", "missing"),
        (500, "Internal Server Error", "server error"),
        (503, "Service Unavailable", "down"),
    ],
)
async def test_fetch_raises_on_http_error(
    monkeypatch: pytest.MonkeyPatch,
    status: int,
    reason: str,
    body: str,
) -> None:
    response = FakeResponse(status=status, reason=reason, text_data=body)

    monkeypatch.setattr(
        "ecb_rate.client.aiohttp.ClientSession",
        lambda **kwargs: FakeSession(response),
    )

    client = ECBJsonClient()

    with pytest.raises(
        EcbApiError,
        match=rf"HTTP error: {status} {reason}\. Response: {body}",
    ):
        await client.fetch(CurrencyType.USD, date(2025, 1, 2))


@pytest.mark.asyncio
async def test_fetch_raises_on_non_json_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request_info = SimpleNamespace(real_url="https://example.invalid")
    content_type_error = aiohttp.ContentTypeError(
        request_info=request_info,
        history=(),
        message="not json",
    )
    response = FakeResponse(text_data="<html>bad</html>", json_exc=content_type_error)

    monkeypatch.setattr(
        "ecb_rate.client.aiohttp.ClientSession",
        lambda **kwargs: FakeSession(response),
    )

    client = ECBJsonClient()

    with pytest.raises(
        EcbApiError,
        match=r"Expected JSON but got different content: <html>bad</html>",
    ):
        await client.fetch(CurrencyType.USD, date(2025, 1, 2))


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [[1, 2, 3], "invalid", 123, None])
async def test_fetch_raises_on_non_object_top_level_json(
    monkeypatch: pytest.MonkeyPatch,
    payload: Any,
) -> None:
    response = FakeResponse(json_data=payload)

    monkeypatch.setattr(
        "ecb_rate.client.aiohttp.ClientSession",
        lambda **kwargs: FakeSession(response),
    )

    client = ECBJsonClient()

    with pytest.raises(
        EcbApiError,
        match=r"Expected JSON object as top-level response\.",
    ):
        await client.fetch(CurrencyType.USD, date(2025, 1, 2))


@pytest.mark.asyncio
async def test_fetch_wraps_client_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_session = FakeSession(get_exc=aiohttp.ClientConnectionError("boom"))

    monkeypatch.setattr(
        "ecb_rate.client.aiohttp.ClientSession",
        lambda **kwargs: fake_session,
    )

    client = ECBJsonClient()

    with pytest.raises(EcbApiError, match=r"Network error: boom"):
        await client.fetch(CurrencyType.USD, date(2025, 1, 2))


@pytest.mark.asyncio
async def test_fetch_wraps_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_session = FakeSession(get_exc=asyncio.TimeoutError())

    monkeypatch.setattr(
        "ecb_rate.client.aiohttp.ClientSession",
        lambda **kwargs: fake_session,
    )

    client = ECBJsonClient()

    with pytest.raises(EcbApiError, match=r"Request timeout\."):
        await client.fetch(CurrencyType.USD, date(2025, 1, 2))