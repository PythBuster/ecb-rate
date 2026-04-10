from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import QueryParams, RatePoint


def test_query_params_accepts_currency_enum() -> None:
    query = QueryParams(
        target_currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )

    assert query.target_currency == CurrencyType.TRY


@pytest.mark.parametrize("currency_input", ["TRY", "try"])
def test_query_params_casts_supported_currency_strings(
    currency_input: str,
) -> None:
    query = QueryParams(
        target_currency=currency_input,  # type: ignore[arg-type]
        specific_date=date(2025, 6, 6),
    )

    assert query.target_currency == CurrencyType.TRY


def test_query_params_rejects_invalid_currency() -> None:
    with pytest.raises(ValidationError):
        QueryParams(
            target_currency="noop",  # type: ignore[arg-type]
            specific_date=date(2025, 6, 6),
        )


def test_rate_point_accepts_decimal_rate() -> None:
    point = RatePoint(
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
        target_currency=CurrencyType.TRY,
    )

    assert point.rate == Decimal("43.1234")


def test_rate_point_casts_string_rate_to_decimal() -> None:
    point = RatePoint(
        date=date(2025, 6, 6),
        rate="43.1234",  # type: ignore[arg-type]
        target_currency=CurrencyType.TRY,
    )

    assert point.rate == Decimal("43.1234")


def test_rate_point_rejects_non_numeric_string_rate() -> None:
    with pytest.raises(ValidationError):
        RatePoint(
            date=date(2025, 6, 6),
            rate="not-a-number",  # type: ignore[arg-type]
            target_currency=CurrencyType.TRY,
        )


def test_rate_point_rejects_none_rate() -> None:
    with pytest.raises(ValidationError):
        RatePoint(
            date=date(2025, 6, 6),
            rate=None,  # type: ignore[arg-type]
            target_currency=CurrencyType.TRY,
        )


def test_rate_point_defaults_base_currency_to_eur() -> None:
    point = RatePoint(
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
        target_currency=CurrencyType.TRY,
    )

    assert point.base_currency == CurrencyType.EUR
