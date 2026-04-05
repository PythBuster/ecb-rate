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

    EUR = "eur"
    TRY = "try"

    @property
    def code(self) -> str:
        """
        Return the ECB-compatible uppercase currency code.
        """
        return self.value.upper()
