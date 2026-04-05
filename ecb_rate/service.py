"""
Business logic for building EUR exchange rates from ECB JSON series.
"""

from datetime import date
from decimal import Decimal
from typing import Any

from ecb_rate.client import ECBJsonClient
from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import EcbApiError, QueryParams, RatePoint, SeriesResult


class EcbJsonParser:
    """
    Parser for ECB SDMX-JSON responses.
    """

    def parse_eur_to_currency_points(
        self,
        payload: dict[str, Any],
        currency: CurrencyType,
    ) -> dict[date, Decimal]:
        """
        Parse a single ECB series into:
            {observation_date: eur_to_currency_rate}
        """
        try:
            time_dimension = payload["structure"]["dimensions"]["observation"][0][
                "values"
            ]
            dataset = payload["dataSets"][0]
            series_map = dataset["series"]
        except (KeyError, IndexError, TypeError) as exc:
            raise EcbApiError("Unexpected ECB JSON structure.") from exc

        if not series_map:
            return {}

        first_series_key = next(iter(series_map))
        observations = series_map[first_series_key].get("observations", {})

        result: dict[date, Decimal] = {}

        for obs_index, obs_payload in observations.items():
            if not obs_payload:
                continue

            try:
                time_idx = int(obs_index)
                obs_date = date.fromisoformat(time_dimension[time_idx]["id"])
                obs_value = Decimal(str(obs_payload[0]))
            except (ValueError, IndexError, KeyError, TypeError) as exc:
                raise EcbApiError(
                    f"Failed to parse observation for currency {currency.code}."
                ) from exc

            result[obs_date] = obs_value

        return result


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

    async def get_rates(self, query: QueryParams) -> SeriesResult:
        """
        Return the EUR -> target currency rate for the requested date.
        """
        parsed = await self._fetch_eur_to_currency(
            currency=query.target_currency,
            specific_date=query.specific_date,
        )

        points = [
            RatePoint(date=obs_date, rate=rate)
            for obs_date, rate in sorted(parsed.items())
        ]

        return SeriesResult(
            base_currency=CurrencyType.EUR,
            target_currency=query.target_currency,
            points=points,
        )

    async def _fetch_eur_to_currency(
        self,
        currency: CurrencyType,
        specific_date: date,
    ) -> dict[date, Decimal]:
        if currency == CurrencyType.EUR:
            return {specific_date: Decimal("1")}

        payload = await self._client.fetch_series(
            currency=currency,
            specific_date=specific_date,
        )
        parsed = self._parser.parse_eur_to_currency_points(
            payload=payload,
            currency=currency,
        )

        if not parsed:
            raise EcbApiError(
                f"No ECB observations found for {currency.code} "
                f"up to {specific_date.isoformat()}."
            )

        return parsed
