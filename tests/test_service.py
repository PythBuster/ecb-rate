import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import EcbApiError, QueryParams
from ecb_rate.service import EcbJsonParser, ExchangeRateService

@pytest.fixture(scope="session")
def payload_json_path():
    return Path(__file__).parent / "test_data" / "payload.json"


class DummyClient:
    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload or {}
        self.calls: list[tuple[date,]] = []

    async def fetch(self, specific_date: date) -> dict:
        self.calls.append((specific_date,))
        return self.payload




def test_parser_parses_valid_payload(payload_json_path) -> None:
    parser = EcbJsonParser()
    payload = json.loads(payload_json_path.read_text())

    result = parser.extract_ecb_rate(payload)

    assert result == Decimal(12.3456)


def test_parser_raises_for_invalid_structure() -> None:
    parser = EcbJsonParser()

    with pytest.raises(EcbApiError, match="Unexpected ECB JSON structure"):
        parser.extract_ecb_rate({})


@pytest.mark.asyncio
async def test_service_returns_identity_for_eur() -> None:
    client = DummyClient()
    parser = EcbJsonParser()
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
    assert client.calls == []  # pylint: disable=use-implicit-booleaness-not-comparison

