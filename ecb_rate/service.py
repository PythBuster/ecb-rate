"""
Business logic for building EUR exchange rates from ECB JSON series.
"""

from datetime import date
from decimal import Decimal
from typing import Any

from ecb_rate.client import ECBJsonClient
from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import EcbApiError, QueryParams, RatePoint


class EcbJsonParser:
    """
    Parser for ECB JSON responses.
    """

    def extract_ecb_rate(
        self,
        payload: dict[str, Any],
    ) -> Decimal:
        """
        Extract the currency rate from ECB JSON payload.
        """

        try:
            result = list(payload["dataSets"][0]["series"].values())[0]["observations"][
                "0"
            ][0]

            if result is None:
                raise EcbApiError("No exchange rate found.")
        except (KeyError, IndexError, TypeError) as exc:
            raise EcbApiError("Unexpected ECB JSON structure.") from exc

        return Decimal(str(result))


class ExchangeRateService:
    """
    High-level service that fetches ECB series and computes:

        1 EUR = X target_currency
    """

    def __init__(
        self,
        client: ECBJsonClient,
        parser: EcbJsonParser,
    ) -> None:
        self._client = client
        self._parser = parser

    async def get_rate(self, query: QueryParams) -> RatePoint:
        """
        Return the EUR -> target currency rate for the requested date.
        """

        if query.target_currency == CurrencyType.EUR:
            return RatePoint(
                target_currency=query.target_currency,
                date=query.specific_date,
                rate=Decimal("1"),
            )

        rate = await self._fetch_eur_to_currency(
            currency=query.target_currency,
            specific_date=query.specific_date,
        )

        return RatePoint(
            target_currency=query.target_currency,
            date=query.specific_date,
            rate=rate,
        )

    async def _fetch_eur_to_currency(
        self,
        currency: CurrencyType,
        specific_date: date,
    ) -> Decimal:
        payload = await self._client.fetch(
            currency=currency,
            specific_date=specific_date,
        )
        return self._parser.extract_ecb_rate(
            payload=payload,
        )
