from datetime import date

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
        json_data: dict | None = None,
        text_data: str = "",
        json_exception: Exception | None = None,
    ) -> None:
        self.status = status
        self.reason = reason
        self._json_data = json_data if json_data is not None else {}
        self._text_data = text_data
        self._json_exception = json_exception

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def json(self):
        if self._json_exception is not None:
            raise self._json_exception
        return self._json_data

    async def text(self):
        return self._text_data


class FakeSession:
    def __init__(self, response: FakeResponse, capture: dict) -> None:
        self._response = response
        self._capture = capture

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    def get(self, url, params=None):
        self._capture["url"] = url
        self._capture["params"] = params
        return self._response


@pytest.mark.asyncio
async def test_fetch_series_success(monkeypatch) -> None:
    capture: dict = {}
    response = FakeResponse(json_data={"foo": "bar"})

    def fake_client_session(*_, **kwargs):
        capture["headers"] = kwargs.get("headers")
        return FakeSession(response, capture)

    monkeypatch.setattr(aiohttp, "ClientSession", fake_client_session)

    client = ECBJsonClient(timeout_seconds=10)
    result = await client.fetch_series(
        currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )

    assert result == {"foo": "bar"}
    assert capture["url"].endswith("/D.TRY.EUR.SP00.A")
    assert capture["params"] == {
        "format": "jsondata",
        "endPeriod": "2025-06-06",
        "lastNObservations": "1",
    }
    assert capture["headers"]["Accept"] == "application/json"


@pytest.mark.asyncio
async def test_fetch_series_raises_on_http_error(monkeypatch) -> None:
    capture: dict = {}
    response = FakeResponse(
        status=500,
        reason="Internal Server Error",
        text_data="boom",
    )

    def fake_client_session(*_, **__):
        return FakeSession(response, capture)

    monkeypatch.setattr(aiohttp, "ClientSession", fake_client_session)

    client = ECBJsonClient()

    with pytest.raises(EcbApiError, match="HTTP error: 500"):
        await client.fetch_series(
            currency=CurrencyType.TRY,
            specific_date=date(2025, 6, 6),
        )


@pytest.mark.asyncio
async def test_fetch_series_raises_on_non_json_response(monkeypatch) -> None:
    capture: dict = {}
    response = FakeResponse(
        json_exception=aiohttp.ContentTypeError(
            request_info=None,
            history=(),
            message="not json",
        ),
        text_data="<html>not json</html>",
    )

    def fake_client_session(*_, **__):
        return FakeSession(response, capture)

    monkeypatch.setattr(aiohttp, "ClientSession", fake_client_session)

    client = ECBJsonClient()

    with pytest.raises(EcbApiError, match="Expected JSON but got different content"):
        await client.fetch_series(
            currency=CurrencyType.TRY,
            specific_date=date(2025, 6, 6),
        )


@pytest.mark.asyncio
async def test_fetch_series_raises_on_non_dict_json(monkeypatch) -> None:
    capture: dict = {}
    response = FakeResponse(json_data=["not", "a", "dict"])

    def fake_client_session(*_, **__):
        return FakeSession(response, capture)

    monkeypatch.setattr(aiohttp, "ClientSession", fake_client_session)

    client = ECBJsonClient()

    with pytest.raises(EcbApiError, match="Expected JSON object as top-level response"):
        await client.fetch_series(
            currency=CurrencyType.TRY,
            specific_date=date(2025, 6, 6),
        )
