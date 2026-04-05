"""
CLI entry point for ecb_rate.

Examples:
    ecb_rate TRY
    ecb_rate try
    ecb_rate TRY --specificDate 2025-06-06
    ecb_rate TRY --pretty
"""

import argparse
import asyncio
import sys
from datetime import date

from pydantic import ValidationError

from ecb_rate.client import ECBJsonClient
from ecb_rate.models import (CliInputError, EcbRateError, QueryParams,
                             SeriesResult)
from ecb_rate.service import EcbJsonParser, ExchangeRateService


class CliApplication:
    """
    Application entry point coordinating argparse and the service layer.
    """

    def __init__(self) -> None:
        client = ECBJsonClient(timeout_seconds=10)
        parser = EcbJsonParser()
        self._service = ExchangeRateService(
            client=client,
            parser=parser,
        )

    def run(self, argv: list[str] | None = None) -> int:
        try:
            args = self._parse_args(argv)
            query = self._build_query(args)
            result = asyncio.run(self._service.get_rates(query))
            self._print_result(result, pretty=args.pretty)
            return 0
        except (CliInputError, EcbRateError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    @staticmethod
    def _parse_args(argv: list[str] | None) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            prog="ecb_rate",
            description="Get ECB JSON EUR exchange rates for a target currency.",
        )

        parser.add_argument(
            "target_currency",
            help="Target currency code, e.g. try or TRY",
        )
        parser.add_argument(
            "--specificDate",
            dest="specific_date",
            default=None,
            help="Specific date in YYYY-MM-DD format. Defaults to today.",
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Pretty print output with metadata.",
        )

        return parser.parse_args(argv)

    @staticmethod
    def _build_query(args: argparse.Namespace) -> QueryParams:
        if args.specific_date is None:
            specific_date = date.today()
        else:
            try:
                specific_date = date.fromisoformat(args.specific_date)
            except ValueError as exc:
                raise CliInputError(
                    f"Invalid --specificDate: {args.specific_date}. Expected YYYY-MM-DD."
                ) from exc

        try:
            return QueryParams(
                target_currency=args.target_currency,
                specific_date=specific_date,
            )
        except (ValidationError, ValueError) as exc:
            raise CliInputError(str(exc)) from exc

    @staticmethod
    def _print_result(result: SeriesResult, pretty: bool = False) -> None:
        if not result.points:
            print("No data available.")
            return

        if not pretty:
            print(result.points[-1].rate)
            return

        print(f"Base currency:   {result.base_currency.code}")
        print(f"Target currency: {result.target_currency.code}")
        print()

        for point in result.points:
            print(
                f"{point.date.isoformat()}: "
                f"1 {result.base_currency.code} = {point.rate} {result.target_currency.code}"
            )


def main() -> int:
    app = CliApplication()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
