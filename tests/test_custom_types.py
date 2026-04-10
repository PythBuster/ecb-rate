from ecb_rate.custom_types import CurrencyType


def test_currency_type_values_are_lowercase() -> None:
    for currency in CurrencyType:
        assert currency.value == currency.value.lower()


def test_currency_type_code_returns_uppercase_value() -> None:
    for currency in CurrencyType:
        assert currency.code == currency.value.upper()