from argparse import Namespace
from datetime import date
from decimal import Decimal

import pytest

import ecb_rate.cli as cli_module
from ecb_rate.cli import CliApplication
from ecb_rate.custom_types import CurrencyType
from ecb_rate.models import CliInputError, EcbApiError, QueryParams, RatePoint


@pytest.mark.parametrize(
    ("argv", "expected_currency", "expected_date", "expected_pretty"),
    [
        (["TRY"], "TRY", None, False),
        (["TRY", "--specificDate", "2025-06-06"], "TRY", "2025-06-06", False),
        (["TRY", "--pretty"], "TRY", None, True),
        (
            ["TRY", "--specificDate", "2025-06-06", "--pretty"],
            "TRY",
            "2025-06-06",
            True,
        ),
    ],
)
def test_parse_args(
    argv: list[str],
    expected_currency: str,
    expected_date: str | None,
    expected_pretty: bool,
) -> None:
    args = CliApplication._parse_args(argv)  # pylint: disable=protected-access

    assert isinstance(args, Namespace)
    assert args.target_currency == expected_currency
    assert args.specific_date == expected_date
    assert args.pretty is expected_pretty


@pytest.mark.parametrize("argv", [[], ["--pretty"]])
def test_parse_args_raises_system_exit_on_missing_required_currency(
    argv: list[str],
) -> None:
    with pytest.raises(SystemExit):
        CliApplication._parse_args(argv)  # pylint: disable=protected-access


def test_build_query_uses_today_if_specific_date_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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

    assert isinstance(query, QueryParams)
    assert query.target_currency == CurrencyType.TRY
    assert query.specific_date == date(2025, 6, 6)


@pytest.mark.parametrize(
    ("target_currency", "specific_date", "match"),
    [
        ("TRY", "06-06-2025", "Invalid --specificDate"),
        ("NOPE", "2025-06-06", "Input should be"),
    ],
)
def test_build_query_raises_on_invalid_input(
    target_currency: str,
    specific_date: str,
    match: str,
) -> None:
    args = Namespace(
        target_currency=target_currency,
        specific_date=specific_date,
        pretty=False,
    )

    with pytest.raises(CliInputError, match=match):
        CliApplication._build_query(args)  # pylint: disable=protected-access


@pytest.mark.parametrize(
    ("pretty", "expected_output"),
    [
        (False, "43.1234\n"),
        (
            True,
            "Base currency:   EUR\n"
            "Target currency: TRY\n"
            "\n"
            "2025-06-06: 1 EUR = 43.1234 TRY\n",
        ),
    ],
)
def test_print_result(
    pretty: bool,
    expected_output: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = RatePoint(
        base_currency=CurrencyType.EUR,
        target_currency=CurrencyType.TRY,
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
    )

    CliApplication._print_result(  # pylint: disable=protected-access
        rate_point=result, pretty=pretty
    )

    captured = capsys.readouterr()
    assert captured.out == expected_output
    assert captured.err == ""


@pytest.mark.parametrize("pretty", [False, True])
def test_run_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    pretty: bool,
) -> None:
    result = RatePoint(
        target_currency=CurrencyType.TRY,
        date=date(2025, 6, 6),
        rate=Decimal("43.1234"),
    )

    app = CliApplication()
    calls: dict[str, object] = {}

    monkeypatch.setattr(
        app,
        "_parse_args",
        lambda argv=None: Namespace(
            target_currency="TRY",
            specific_date="2025-06-06",
            pretty=pretty,
        ),
    )

    original_print_result = app._print_result  # pylint: disable=protected-access

    def wrapped_print_result(rate_point: RatePoint, *, pretty: bool) -> None:
        calls["pretty"] = pretty
        calls["result"] = rate_point
        original_print_result(rate_point, pretty=pretty)

    async def fake_get_rate(query: QueryParams):
        calls["query"] = query
        return result

    monkeypatch.setattr(app, "_print_result", wrapped_print_result)
    monkeypatch.setattr(
        app._service, "get_rate", fake_get_rate  # pylint: disable=protected-access
    )

    exit_code = app.run([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert calls["pretty"] is pretty
    assert calls["result"] == result
    assert isinstance(calls["query"], QueryParams)

    if pretty:
        assert "Base currency:   EUR" in captured.out
        assert "2025-06-06: 1 EUR = 43.1234 TRY" in captured.out
    else:
        assert captured.out == "43.1234\n"


@pytest.mark.parametrize(
    ("patch_target", "exc"),
    [
        ("build_query", CliInputError("bad input")),
        ("get_rate", EcbApiError("api down")),
    ],
)
def test_run_returns_error_code_for_known_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    patch_target: str,
    exc: Exception,
) -> None:
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

    if patch_target == "build_query":

        def raise_build_query_error(_args):
            raise exc

        monkeypatch.setattr(app, "_build_query", raise_build_query_error)
    else:

        async def raise_service_error(_query):
            raise exc

        monkeypatch.setattr(
            app._service,  # pylint: disable=protected-access
            "get_rate",
            raise_service_error,
        )

    exit_code = app.run([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == f"Error: {exc}\n"


def test_main_delegates_to_application(monkeypatch: pytest.MonkeyPatch) -> None:
    called: dict[str, object] = {}

    def fake_run(_, argv=None):
        called["called"] = True
        called["argv"] = argv
        return 7

    monkeypatch.setattr(CliApplication, "run", fake_run)

    assert cli_module.main() == 7
    assert called["called"] is True
