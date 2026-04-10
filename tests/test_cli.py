from argparse import Namespace
from datetime import date
from decimal import Decimal

import pytest

import ecb_rate.cli as cli_module
from ecb_rate.cli import CliApplication
from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import CliInputError, QueryParams, RatePoint


def test_build_query_defaults_to_today(monkeypatch) -> None:
    fake_today = date(2025, 6, 6)

    class FakeDate(date):
        @classmethod
        def today(cls):
            return fake_today

    monkeypatch.setattr(cli_module, "date", FakeDate)

    args = Namespace(
        target_currency="TRY",
        specific_date=None,
        pretty=False,
    )

    query = CliApplication._build_query(args)  # pylint: disable=protected-access

    assert isinstance(query, QueryParams)
    assert query.target_currency == CurrencyType.TRY
    assert query.specific_date == fake_today


def test_build_query_parses_specific_date() -> None:
    args = Namespace(
        target_currency="TRY",
        specific_date="2025-06-06",
        pretty=False,
    )

    query = CliApplication._build_query(args)  # pylint: disable=protected-access

    assert query.target_currency == CurrencyType.TRY
    assert query.specific_date == date(2025, 6, 6)


def test_build_query_raises_on_invalid_date() -> None:
    args = Namespace(
        target_currency="TRY",
        specific_date="06-06-2025",
        pretty=False,
    )

    with pytest.raises(CliInputError, match="Invalid --specificDate"):
        CliApplication._build_query(args)  # pylint: disable=protected-access


def test_parse_args_minimal() -> None:
    args = CliApplication._parse_args(["TRY"])  # pylint: disable=protected-access

    assert isinstance(args, Namespace)
    assert args.target_currency == "TRY"
    assert args.specific_date is None
    assert args.pretty is False


def test_parse_args_with_date() -> None:
    args = CliApplication._parse_args(  # pylint: disable=protected-access
        ["TRY", "--specificDate", "2025-06-06"]
    )

    assert args.target_currency == "TRY"
    assert args.specific_date == "2025-06-06"
    assert args.pretty is False


def test_parse_args_with_pretty_flag() -> None:
    args = CliApplication._parse_args(  # pylint: disable=protected-access
        ["TRY", "--pretty"]
    )

    assert args.target_currency == "TRY"
    assert args.pretty is True


def test_parse_args_with_all_options() -> None:
    args = CliApplication._parse_args(  # pylint: disable=protected-access
        ["TRY", "--specificDate", "2025-06-06", "--pretty"]
    )

    assert args.target_currency == "TRY"
    assert args.specific_date == "2025-06-06"
    assert args.pretty is True


def test_print_result_raw(capsys) -> None:
    result = RatePoint(
        base_currency=CurrencyType.EUR,
        target_currency=CurrencyType.TRY,
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
    )

    CliApplication._print_result(  # pylint: disable=protected-access
        result, pretty=False
    )

    captured = capsys.readouterr()
    assert captured.out.strip() == "43.1234"


def test_print_result_pretty(capsys) -> None:
    result = RatePoint(
        base_currency=CurrencyType.EUR,
        target_currency=CurrencyType.TRY,
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
    )

    CliApplication._print_result(  # pylint: disable=protected-access
        result, pretty=True
    )

    captured = capsys.readouterr()
    assert "Base currency:   EUR" in captured.out
    assert "Target currency: TRY" in captured.out
    assert "2025-06-06: 1 EUR = 43.1234 TRY" in captured.out


def test_print_result_pretty_exact_output(capsys) -> None:
    result = RatePoint(
        base_currency=CurrencyType.EUR,
        target_currency=CurrencyType.TRY,
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
    )

    CliApplication._print_result(  # pylint: disable=protected-access
        result, pretty=True
    )

    captured = capsys.readouterr()
    assert captured.out == (
        "Base currency:   EUR\n"
        "Target currency: TRY\n"
        "\n"
        "2025-06-06: 1 EUR = 43.1234 TRY\n"
    )

def test_run_success(monkeypatch, capsys) -> None:
    result = RatePoint(
        base_currency=CurrencyType.EUR,
        target_currency=CurrencyType.TRY,
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
    )

    app = CliApplication()

    monkeypatch.setattr(
        app,
        "_parse_args",
        lambda argv=None: Namespace(
            target_currency="TRY",
            specific_date="2025-06-06",
            pretty=False,
        ),
    )

    async def fake_get_rate(_):
        return result

    monkeypatch.setattr(
        app._service,  # pylint: disable=protected-access
        "get_rate",
        fake_get_rate,
    )

    exit_code = app.run([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "43.1234"


def test_run_success_pretty(monkeypatch, capsys) -> None:
    result = RatePoint(
        target_currency=CurrencyType.TRY,
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
    )

    app = CliApplication()

    monkeypatch.setattr(
        app,
        "_parse_args",
        lambda argv=None: Namespace(
            target_currency="TRY",
            specific_date="2025-06-06",
            pretty=True,
        ),
    )

    async def fake_get_rate(_):
        return result

    monkeypatch.setattr(
        app._service,  # pylint: disable=protected-access
        "get_rate",
        fake_get_rate,
    )

    exit_code = app.run([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == (
        "Base currency:   EUR\n"
        "Target currency: TRY\n"
        "\n"
        "2025-06-06: 1 EUR = 43.1234 TRY\n"
    )


def test_run_error(monkeypatch, capsys) -> None:
    app = CliApplication()

    def fake_parse_args(_=None):
        return Namespace(
            target_currency="TRY",
            specific_date="bad-date",
            pretty=False,
        )

    monkeypatch.setattr(app, "_parse_args", fake_parse_args)

    exit_code = app.run([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error:" in captured.err
