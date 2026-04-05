from datetime import date
from decimal import Decimal

import pytest

from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import EcbApiError, QueryParams
from ecb_rate.service import EcbJsonParser, ExchangeRateService


class DummyClient:
    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload or {}
        self.calls: list[tuple[CurrencyType, date]] = []

    async def fetch_series(self, currency: CurrencyType, specific_date: date) -> dict:
        self.calls.append((currency, specific_date))
        return self.payload


def make_valid_payload() -> dict:
    return {
        "structure": {
            "dimensions": {
                "observation": [
                    {
                        "id": "TIME_PERIOD",
                        "values": [
                            {"id": "2025-06-06"},
                        ],
                    }
                ]
            }
        },
        "dataSets": [
            {
                "series": {
                    "0:0:0:0:0": {
                        "observations": {
                            "0": [Decimal("43.1234")],
                        }
                    }
                }
            }
        ],
    }


def test_parser_parses_valid_payload() -> None:
    parser = EcbJsonParser()
    payload = make_valid_payload()

    result = parser.parse_eur_to_currency_points(payload, CurrencyType.TRY)

    assert result == {date(2025, 6, 6): Decimal("43.1234")}


def test_parser_returns_empty_dict_for_empty_series_map() -> None:
    parser = EcbJsonParser()
    payload = {
        "structure": {
            "dimensions": {
                "observation": [
                    {
                        "values": [{"id": "2025-06-06"}],
                    }
                ]
            }
        },
        "dataSets": [{"series": {}}],
    }

    result = parser.parse_eur_to_currency_points(payload, CurrencyType.TRY)

    assert result == {}  # pylint: disable=use-implicit-booleaness-not-comparison


def test_parser_raises_for_invalid_structure() -> None:
    parser = EcbJsonParser()

    with pytest.raises(EcbApiError, match="Unexpected ECB JSON structure"):
        parser.parse_eur_to_currency_points({}, CurrencyType.TRY)


@pytest.mark.asyncio
async def test_service_returns_identity_for_eur() -> None:
    client = DummyClient()
    parser = EcbJsonParser()
    service = ExchangeRateService(client=client, parser=parser)

    query = QueryParams(
        target_currency=CurrencyType.EUR,
        specific_date=date(2025, 6, 6),
    )

    result = await service.get_rates(query)

    assert result.base_currency == CurrencyType.EUR
    assert result.target_currency == CurrencyType.EUR
    assert len(result.points) == 1
    assert result.points[0].date == date(2025, 6, 6)
    assert result.points[0].rate == Decimal("1")
    assert client.calls == []  # pylint: disable=use-implicit-booleaness-not-comparison


@pytest.mark.asyncio
async def test_service_fetches_and_returns_try_rate() -> None:
    client = DummyClient(payload=make_valid_payload())
    parser = EcbJsonParser()
    service = ExchangeRateService(client=client, parser=parser)

    query = QueryParams(
        target_currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )

    result = await service.get_rates(query)

    assert client.calls == [(CurrencyType.TRY, date(2025, 6, 6))]
    assert result.base_currency == CurrencyType.EUR
    assert result.target_currency == CurrencyType.TRY
    assert len(result.points) == 1
    assert result.points[0].date == date(2025, 6, 6)
    assert result.points[0].rate == Decimal("43.1234")


@pytest.mark.asyncio
async def test_service_raises_when_no_points_found() -> None:
    payload = {
        "structure": {
            "dimensions": {
                "observation": [
                    {
                        "values": [{"id": "2025-06-06"}],
                    }
                ]
            }
        },
        "dataSets": [{"series": {}}],
    }
    client = DummyClient(payload=payload)
    parser = EcbJsonParser()
    service = ExchangeRateService(client=client, parser=parser)

    query = QueryParams(
        target_currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )

    with pytest.raises(EcbApiError, match="No ECB observations found"):
        await service.get_rates(query)


def test_parser_skips_none_observation_payload() -> None:
    parser = EcbJsonParser()
    payload = {
        "structure": {
            "dimensions": {
                "observation": [
                    {
                        "values": [
                            {"id": "2025-06-06"},
                            {"id": "2025-06-07"},
                        ],
                    }
                ]
            }
        },
        "dataSets": [
            {
                "series": {
                    "0:0:0:0:0": {
                        "observations": {
                            "0": None,
                            "1": [Decimal("43.5678")],
                        }
                    }
                }
            }
        ],
    }

    result = parser.parse_eur_to_currency_points(payload, CurrencyType.TRY)

    assert result == {
        date(2025, 6, 7): Decimal("43.5678"),
    }
