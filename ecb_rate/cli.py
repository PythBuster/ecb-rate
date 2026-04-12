"""
CLI entry point for ecb_rate.

Examples:
    ecb_rate TRY
    ecb_rate try
    ecb_rate TRY --specific-date 2025-06-06
    ecb_rate TRY --pretty
"""

import argparse
import asyncio
import sys
from datetime import date

from pydantic import ValidationError
from importlib.metadata import metadata

from ecb_rate.client import ECBJsonClient
from ecb_rate.models import CliInputError, EcbRateError, QueryParams, RatePoint
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
            result = asyncio.run(self._service.get_rate(query))
            self._print_result(result, pretty=args.pretty)
            return 0
        except (CliInputError, EcbRateError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    @staticmethod
    def _parse_args(argv: list[str] | None) -> argparse.Namespace:
        package_metadata = metadata("ecb-rate")

        project_name = package_metadata["Name"].replace("-", "_")
        project_version = package_metadata["Version"]
        project_description = package_metadata["Summary"]

        parser = argparse.ArgumentParser(
            prog=project_name,
            description=project_description,
        )

        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {project_version}",
            help="Show the installed CLI version and exit.",
        )
        parser.add_argument(
            "target_currency",
            nargs="?",
            help="Target currency code, for example TRY or USD.",
        )
        parser.add_argument(
            "--specific-date",
            dest="specific_date",
            default=None,
            help="Specific date in YYYY-MM-DD format. Defaults to today.",
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Print formatted output with base currency, target currency, and rate date.",
        )

        args = parser.parse_args(argv)

        if args.target_currency is None:
            parser.error("the following arguments are required: target_currency")

        return args

    @staticmethod
    def _build_query(args: argparse.Namespace) -> QueryParams:
        if args.specific_date is None:
            specific_date = date.today()
        else:
            try:
                specific_date = date.fromisoformat(args.specific_date)
            except ValueError as exc:
                raise CliInputError(
                    f"Invalid --specific-date: {args.specific_date}. Expected YYYY-MM-DD."
                ) from exc

        try:
            return QueryParams(
                target_currency=args.target_currency,
                specific_date=specific_date,
            )
        except (ValidationError, ValueError) as exc:
            raise CliInputError(str(exc)) from exc

    @staticmethod
    def _print_result(rate_point: RatePoint, pretty: bool = False) -> None:
        if not pretty:
            print(f"{rate_point.rate:.4f}")
            return

        print(f"Base currency:   {rate_point.base_currency.code}")
        print(f"Target currency: {rate_point.target_currency.code}")
        print()

        print(
            f"{rate_point.date.isoformat()}: "
            f"1 {rate_point.base_currency.code} = {rate_point.rate:.4f} {rate_point.target_currency.code}"
        )


def main() -> int:
    app = CliApplication()
    return app.run()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
