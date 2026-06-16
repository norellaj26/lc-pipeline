import pandas as pd
from typing import Any, List

from models.validation_error import ValidationError
from validators.base import BaseValidator
from config.validation_rules import SWIFT_RULES
from config.constants import PATTERNS


class SwiftValidator(BaseValidator):
    """Validates SWIFT/BIC codes."""

    def _validate(self, field: str, value: Any, **context) -> None:
        # Gate 1: Present?
        if value is None or pd.isna(value):
            self._add_error('BIC001', field=field, value=value)
            return

        str_value = str(value).strip()
        if str_value == '':
            self._add_error('BIC001', field=field, value=value)
            return

        # Gate 2: Correct length? (SWIFT BIC is either 8 or 11 characters)
        valid_length = SWIFT_RULES['valid_lengths']
        if len(str_value) not in valid_length:
            self._add_error('BIC002', field=field, value=str_value)
            return

        # Gate 3: Matches format?
        swift_pattern = PATTERNS['swift_bic']
        if not swift_pattern.match(str_value):
            self._add_error('BIC003', field=field, value=str_value)
            return

        # Gates passed — valid SWIFT format
