from validators.api.gleif_client import GleifClient
import pandas as pd
from typing import Any
from validators.base import BaseValidator
from config.validation_rules import LEI_RULES
from config.constants import PATTERNS

class LeiValidator(BaseValidator):
    """Validates Legal Entity Identifier (LEI) codes."""

    def __init__(self) -> None:
        super().__init__()
        self._gleif_client = GleifClient()

    def _validate(self, field: str, value, **context) -> None:
        ## Gate 1: Present?
        if value is None or pd.isna(value):
            self._add_error('LEI001', field=field, value=value)
            return

        str_value = str(value).strip()

        ## Gate 2: Correct length?
        expected_length = LEI_RULES['length']
        if len(str_value) != expected_length:
            self._add_error('LEI002', field=field, value=str_value)
            return

        ## Gate 3: Matches format?
        # LEI format: 4 alphanumeric prefix + 14 alphanumeric + 2 digit checksum
        lei_pattern = PATTERNS['Lei']
        if not lei_pattern.match(str_value):
            self._add_error('LEI003', field=field, value=str_value)
            return

        ## Gate 4: Known to GLEIF?
        result = self._gleif_client.lookup(str_value)

        if result['status'] == 'NOT_FOUND':
            self._add_error('LEI004', field=field, value=str_value)
        elif result['status'] == 'INACTIVE':
            self._add_error('LEI005', field=field, value=str_value)
        elif result['status'] == 'ERROR':
            self._add_error('LEI006', field=field, value=str_value)




























































