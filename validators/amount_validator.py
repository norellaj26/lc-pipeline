import re
import pandas as pd
from decimal import Decimal
from typing import Any
from validators.base import BaseValidator
from config.validation_rules import AMOUNT_RULES
from config.constants import CURRENCY_INFO


class AmountValidator(BaseValidator):
    """Validates LC transaction amounts."""

    def _validate(self, field: str, value: Any, **context) -> None:
        ## Phase 1: Can I even read this? / Format check
        clean_value = self._check_format(field, value)
        if clean_value is None:
            return

        ## Phase 2: Is the number valid? / Value check -> Passes the cleaned value
        self._check_value(field, clean_value, **context)

    def _check_format(self, field: str, value: Any):  # The Gatekeeper
        # Check 1: Is it even a string or number we can work with?
        if value is None or pd.isna(value):
            self._add_error('AMT005', field=field, value=value)
            return None
        str_value = str(value).strip()

        # Check 2: Is it completely non-numeric garbage?
        if not self._is_numeric_format(str_value):
            self._add_error('AMT005', field=field, value=value)
            return None

        # Check 3: If it has commas, are they in the right places?
        if ',' in str_value and not self._is_valid_comma_format(str_value):
            self._add_error('AMT005', field=field, value=value)
            return None

        # All format checks passed — strip commas and return clean Decimal
        clean_str = str_value.replace(',', '')
        return Decimal(clean_str)

    @staticmethod  # These methods don't need anything from the instance
    def _is_numeric_format(value: str) -> bool:
        # Can this string become a number? (allows commas, dots, leading sign)
        if not value:
            return False

        # First character can be digit or sign
        if value[0] not in '0123456789-':
            return False

        # Rest can only be digits, commas, dots
        return all(c in '0123456789,.' for c in value[1:])

    @staticmethod
    def _is_valid_comma_format(value: str) -> bool:
        # Are commas in the right places? (thousands separator pattern)"""
        pattern = r'^-?\d{1,3}(,\d{3})*(\.\d+)?$'
        return bool(re.match(pattern, value))

    def _check_value(self, field: str, amount, **context) -> None:
        # Phase 2: Is the number valid?

        # Check 1: Zero
        if amount == Decimal('0'):
            self._add_error('AMT001', field=field, value=str(amount))
        # Check 2: Negative
        elif amount < Decimal('0'):
            self._add_error('AMT002', field=field, value=str(amount))
        # Check 3: Exceeds maximum
        max_value = AMOUNT_RULES['max_value']
        if amount > max_value:
            self._add_error('AMT003', field=field, value=str(amount))
        # Check 4: Decimal places vs currency
        currency = context.get('currency')
        if isinstance(currency, str):
            self._check_decimals(field, amount, currency)

    def _check_decimals(self, field: str, amount, currency: str) -> None:
        # Check decimal places match currency requirements.
        currency_upper = currency.upper()
        currency_info = CURRENCY_INFO.get(currency_upper)
        if not currency_info:
            return  # Unknown currency

        expected_decimals = currency_info['decimals']

        # as_tuple() returns (sign, digits, exponent); exponent is negative for decimals
        # e.g. Decimal('12.345') → exponent=-3, so actual decimal places = 3
        sign, digits, exponent = amount.as_tuple()
        actual_decimals = max(0, -exponent)

        if actual_decimals > expected_decimals:
            self._add_error('AMT006', field=field, value=str(amount))
























        