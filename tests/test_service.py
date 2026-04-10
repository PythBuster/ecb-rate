from datetime import date
from decimal import Decimal
import json
from pathlib import Path
from typing import Any

import pytest

from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import EcbApiError, QueryParams
from ecb_rate.service import EcbJsonParser, ExchangeRateService


@pytest.fixture(scope="session")
def payload_json_path() -> Path:
    return Path(__file__).parent / "test_data" / "payload.json"


class DummyClient:
    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self.payload = payload or {}
        self.calls: list[tuple[CurrencyType, date]] = []

    async def fetch(self, currency: CurrencyType, specific_date: date) -> dict[str, Any]:
        self.calls.append((currency, specific_date))
        return self.payload


class DummyParser:
    def __init__(self, result: Decimal = Decimal("43.1234")) -> None:
        self.result = result
        self.payloads: list[dict[str, Any]] = []

    def extract_ecb_rate(self, payload: dict[str, Any]) -> Decimal:
        self.payloads.append(payload)
        return self.result


def test_parser_parses_valid_payload_exact_decimal(payload_json_path: Path) -> None:
    parser = EcbJsonParser()
    payload = json.loads(payload_json_path.read_text())

    result = parser.extract_ecb_rate(payload)

    assert result == Decimal("12.3456")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"dataSets": []},
        {"dataSets": [{"series": {}}]},
        {"dataSets": [{"series": {"0:0:0:0:0": {}}}]},
        {"dataSets": [{"series": {"0:0:0:0:0": {"observations": {}}}}]},
        {"dataSets": [{"series": {"0:0:0:0:0": {"observations": {"0": []}}}}]},
        {"dataSets": None},
    ],
)
def test_parser_raises_generic_error_for_invalid_payload_shapes(
    payload: dict[str, Any],
) -> None:
    parser = EcbJsonParser()

    with pytest.raises(EcbApiError, match="Unexpected ECB JSON structure"):
        parser.extract_ecb_rate(payload)


@pytest.mark.asyncio
async def test_service_returns_identity_for_eur() -> None:
    client = DummyClient()
    parser = DummyParser()
    service = ExchangeRateService(client=client, parser=parser)

    query = QueryParams(
        target_currency=CurrencyType.EUR,
        specific_date=date(2025, 6, 6),
    )

    result = await service.get_rate(query)

    assert result.base_currency == CurrencyType.EUR
    assert result.target_currency == CurrencyType.EUR
    assert result.date == date(2025, 6, 6)
    assert result.rate == Decimal("1")
    assert client.calls == []
    assert parser.payloads == []


@pytest.mark.asyncio
async def test_service_fetches_and_parses_non_eur_currency() -> None:
    payload = {"dummy": "payload"}
    client = DummyClient(payload=payload)
    parser = DummyParser(result=Decimal("43.1234"))
    service = ExchangeRateService(client=client, parser=parser)

    query = QueryParams(
        target_currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )

    result = await service.get_rate(query)

    assert result.base_currency == CurrencyType.EUR
    assert result.target_currency == CurrencyType.TRY
    assert result.date == date(2025, 6, 6)
    assert result.rate == Decimal("43.1234")
    assert client.calls == [(CurrencyType.TRY, date(2025, 6, 6))]
    assert parser.payloads == [payload]


@pytest.mark.asyncio
async def test_service_propagates_client_error() -> None:
    class FailingClient:
        async def fetch(self, currency: CurrencyType, specific_date: date) -> dict[str, Any]:
            raise EcbApiError("network down")

    parser = DummyParser()
    service = ExchangeRateService(client=FailingClient(), parser=parser)

    query = QueryParams(
        target_currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )

    with pytest.raises(EcbApiError, match="network down"):
        await service.get_rate(query)


@pytest.mark.asyncio
async def test_service_propagates_parser_error() -> None:
    class FailingParser:
        def extract_ecb_rate(self, payload: dict[str, Any]) -> Decimal:
            raise EcbApiError("bad payload")

    payload = {"dummy": "payload"}
    client = DummyClient(payload=payload)
    service = ExchangeRateService(client=client, parser=FailingParser())

    query = QueryParams(
        target_currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )

    with pytest.raises(EcbApiError, match="bad payload"):
        await service.get_rate(query)


def test_parser_raises_when_observation_value_is_none() -> None:
    parser = EcbJsonParser()
    payload = {
        "dataSets": [
            {
                "series": {
                    "0:0:0:0:0": {
                        "observations": {
                            "0": [None],
                        }
                    }
                }
            }
        ]
    }

    with pytest.raises(EcbApiError, match=r"No exchange rate found\."):
        parser.extract_ecb_rate(payload)