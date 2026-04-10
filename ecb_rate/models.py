"""
Shared models and exceptions for ecb_rate.
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, field_validator

from ecb_rate.custom_types import CurrencyType


class EcbRateError(Exception):
    """Base exception for the application."""


class CliInputError(EcbRateError):
    """Raised when CLI input is invalid."""


class EcbApiError(EcbRateError):
    """Raised when the ECB API request or response is invalid."""


class QueryParams(BaseModel):
    """
    Query parameters for the currency conversion request.

    EUR is always the base currency.
    """

    target_currency: CurrencyType
    specific_date: date

    @field_validator("target_currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        """
        Normalize currency input to lowercase before enum validation.
        """
        if isinstance(value, str) and not isinstance(value, CurrencyType):
            return value.lower()

        return value


class RatePoint(BaseModel):
    """
    A single exchange-rate result for a specific date.
    """

    date: date
    rate: Decimal
    target_currency: CurrencyType
    base_currency: CurrencyType = CurrencyType.EUR

