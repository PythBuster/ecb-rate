"""
ECB-specific async JSON API client.
"""

from datetime import date
from typing import Any

import aiohttp

from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import EcbApiError


class ECBJsonClient:
    """
    Async HTTP client for the ECB Data Portal API.

    This client is responsible for:
    - building ECB-specific URLs
    - executing HTTP requests
    - returning parsed JSON responses
    """

    BASE_URL = "https://data-api.ecb.europa.eu/service/data/EXR"

    def __init__(self, timeout_seconds: int = 10) -> None:
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async def fetch(
        self,
        currency: CurrencyType,
        specific_date: date,
    ) -> dict[str, Any]:
        """
        Fetch ECB time series data in jsondata format for a specific date.

        Uses:
            D.<CURRENCY>.EUR.SP00.A
            format=jsondata
            lastNObservations=1
            endPeriod=<date>
            details=dataonly

        This returns the latest available observation up to the given date.
        """
        series_key = f"D.{currency.code}.EUR.SP00.A"

        iso_formatted_date = specific_date.isoformat()
        params = {
            "format": "jsondata",
            "lastNObservations": 1,
            "endPeriod": iso_formatted_date,
            "details": "dataonly",
        }

        headers = {
            "Accept": "application/json",
            "User-Agent": "ecb_rate/0.1.0",
        }

        url = f"{self.BASE_URL}/{series_key}"

        try:
            async with aiohttp.ClientSession(
                timeout=self._timeout,
                headers=headers,
            ) as session:
                async with session.get(url, params=params) as response:
                    if response.status >= 400:
                        text = await response.text()
                        raise EcbApiError(
                            f"HTTP error: {response.status} {response.reason}. "
                            f"Response: {text}"
                        )

                    try:
                        data = await response.json()

                    except aiohttp.ContentTypeError as exc:
                        text = await response.text()
                        raise EcbApiError(
                            f"Expected JSON but got different content: {text}"
                        ) from exc

                    if not isinstance(data, dict):
                        raise EcbApiError("Expected JSON object as top-level response.")

                    return data

        except aiohttp.ClientError as exc:
            raise EcbApiError(f"Network error: {exc}") from exc
        except TimeoutError as exc:
            raise EcbApiError("Request timeout.") from exc
