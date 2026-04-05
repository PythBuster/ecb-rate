from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import QueryParams, RatePoint, SeriesResult


def test_query_params_normalizes_currency_to_lowercase() -> None:
    query = QueryParams(
        target_currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )
    assert query.target_currency == CurrencyType.TRY


def test_query_params_normalizes_currency_to_lowercase_str_conversion() -> None:
    query = QueryParams(
        target_currency="TRY",  # type: ignore[arg-type]
        specific_date=date(2025, 6, 6),
    )
    assert query.target_currency == CurrencyType.TRY


def test_query_params_accepts_lowercase_currency() -> None:
    query = QueryParams(
        target_currency=CurrencyType.TRY,
        specific_date=date(2025, 6, 6),
    )
    assert query.target_currency == CurrencyType.TRY


def test_query_params_accepts_lowercase_currency_str_conversion() -> None:
    query = QueryParams(
        target_currency="try",  # type: ignore[arg-type]
        specific_date=date(2025, 6, 6),
    )
    assert query.target_currency == CurrencyType.TRY


def test_query_params_rejects_invalid_currency_str_conversion() -> None:
    with pytest.raises(ValidationError):
        QueryParams(
            target_currency="usd",  # type: ignore[arg-type]
            specific_date=date(2025, 6, 6),
        )


def test_rate_point_model() -> None:
    point = RatePoint(date=date(2025, 6, 6), rate=Decimal("43.1234"))
    assert point.date == date(2025, 6, 6)
    assert point.rate == Decimal("43.1234")


def test_rate_point_accepts_str_conversion() -> None:
    point = RatePoint(date=date(2025, 6, 6), rate="43.1234")  # type: ignore[arg-type]
    assert point.rate == Decimal("43.1234")


def test_series_result_model() -> None:
    result = SeriesResult(
        base_currency=CurrencyType.EUR,
        target_currency=CurrencyType.TRY,
        points=[
            RatePoint(date=date(2025, 6, 6), rate=Decimal("43.1234")),
        ],
    )
    assert result.base_currency == CurrencyType.EUR
    assert result.target_currency == CurrencyType.TRY
    assert len(result.points) == 1


def test_series_result_model_str_conversion() -> None:
    result = SeriesResult(
        base_currency=CurrencyType.EUR,
        target_currency=CurrencyType.TRY,
        points=[
            RatePoint(date=date(2025, 6, 6), rate="43.1234"),  # type: ignore[arg-type]
        ],
    )
    assert result.base_currency == CurrencyType.EUR
    assert result.target_currency == CurrencyType.TRY
    assert len(result.points) == 1
