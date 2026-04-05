"""
Custom shared types for ecb_rate.
"""

from enum import StrEnum


class CurrencyType(StrEnum):
    """
    Supported currencies for the CLI.

    Values are stored in lowercase. Use ``code`` for the ECB-compatible
    uppercase representation.
    """

    AUD = "aud"
    # Australian dollar (Australia)

    BRL = "brl"
    # Brazilian real (Brazil)

    CAD = "cad"
    # Canadian dollar (Canada)

    CHF = "chf"
    # Swiss franc (Switzerland)

    CNY = "cny"
    # Chinese yuan (China)

    CZK = "czk"
    # Czech koruna (Czech Republic)

    DKK = "dkk"
    # Danish krone (Denmark)

    EUR = "eur"
    # Euro (Eurozone)

    GBP = "gbp"
    # Pound sterling (United Kingdom)

    HKD = "hkd"
    # Hong Kong dollar (Hong Kong)

    HUF = "huf"
    # Hungarian forint (Hungary)

    IDR = "idr"
    # Indonesian rupiah (Indonesia)

    ILS = "ils"
    # Israeli shekel (Israel)

    INR = "inr"
    # Indian rupee (India)

    ISK = "isk"
    # Icelandic krona (Iceland)

    JPY = "jpy"
    # Japanese yen (Japan)

    KRW = "krw"
    # South Korean won (South Korea)

    MXN = "mxn"
    # Mexican peso (Mexico)

    MYR = "myr"
    # Malaysian ringgit (Malaysia)

    NOK = "nok"
    # Norwegian krone (Norway)

    NZD = "nzd"
    # New Zealand dollar (New Zealand)

    PHP = "php"
    # Philippine peso (Philippines)

    PLN = "pln"
    # Polish zloty (Poland)

    RON = "ron"
    # Romanian leu (Romania)

    SEK = "sek"
    # Swedish krona (Sweden)

    SGD = "sgd"
    # Singapore dollar (Singapore)

    THB = "thb"
    # Thai baht (Thailand)

    TRY = "try"
    # Turkish lira (Turkey)

    USD = "usd"
    # US dollar (United States)

    ZAR = "zar"
    # South African rand (South Africa)

    @property
    def code(self) -> str:
        """
        Return the ECB-compatible uppercase currency code.
        """
        return self.value.upper()
