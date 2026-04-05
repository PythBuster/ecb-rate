from ecb_rate.custom_types import CurrencyType


def test_currency_code_returns_uppercase() -> None:
    assert CurrencyType.EUR.code == "EUR"
    assert CurrencyType.TRY.code == "TRY"


def test_currency_values_are_lowercase() -> None:
    assert CurrencyType.EUR.value == "eur"
    assert CurrencyType.TRY.value == "try"
