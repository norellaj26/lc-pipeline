import pandas as pd
from typing import Any
from validators.base import BaseValidator
from config.validation_rules import LC_RULES
from config.constants import LC_FORMS, AVAILABLE_WITH_OPTIONS, CONFIRMATION_STATUSES


class LcValidator(BaseValidator):
    """Validates LC document fields."""

    def _validate(self, field: str, value: Any, **context) -> None:
        # value = lc_number (the primary field)
        self._check_lc_number(field, value)

        lc_form = context.get('lc_form')
        self._check_lc_form(lc_form)

        available_with = context.get('available_with')
        self._check_available_with(available_with)

        confirmation_status = context.get('confirmation_status')
        confirmation_bank_swift = context.get('confirmation_bank_swift')
        self._check_confirmation(confirmation_status, confirmation_bank_swift)

    def _check_lc_number(self, field: str, value: Any) -> None:
        """Check LC number: present, length."""

        # Gate 1: Present?
        if value is None or pd.isna(value):
            self._add_error('LC001', field=field, value=value)
            return

        str_value = str(value).strip()
        if str_value == '':
            self._add_error('LC001', field, value)
            return

        # Gate 2: Too short?
        min_length = LC_RULES['lc_number_min_length']
        if len(str_value) < min_length:
            self._add_error('LC002', field=field, value=str_value)

        # Gate 3: Too long?
        max_len = LC_RULES['lc_number_max_length']
        if len(str_value) > max_len:
            self._add_error('LC003', field=field, value=str_value)

    def _check_lc_form(self, lc_form: Any) -> None:
        """Check LC form against valid options."""

        if lc_form is None or pd.isna(lc_form):
            self._add_error('LC004', field='lc_form', value=lc_form)
            return

        str_value = str(lc_form).strip()
        if str_value not in LC_FORMS:
            self._add_error('LC004', field='lc_form', value=str_value)

    def _check_available_with(self, available_with: Any) -> None:
        """Check available_with against valid options."""

        if available_with is None or pd.isna(available_with):
            self._add_error('LC005', field='available_with', value=available_with)
            return

        str_value = str(available_with).strip()
        if str_value not in AVAILABLE_WITH_OPTIONS:
            self._add_error('LC005', field='available_with', value=str_value)

    ## Check 1: Is the confirmation status valid? (CONFIRMED, UNCONFIRMED — not MAYBE)
    ## Check 2: If status is CONFIRMED, is there actually a confirming bank SWIFT?
    def _check_confirmation(self, status: Any, confirming_swift: Any) -> None:
        """Check confirmation status and confirming bank consistency."""

        # Check 1: Valid status?
        if status is None or pd.isna(status):
            self._add_error('LC008', field='confirmation_status', value=status)
            return

        str_status = str(status).strip()
        if str_status not in CONFIRMATION_STATUSES:
            self._add_error('LC008', field='confirmation_status', value=str_status)
            return

        # Check 2: CONFIRMED but no bank?
        if str_status == 'CONFIRMED':
            if confirming_swift is None or pd.isna(confirming_swift):
                self._add_error('LC007', field='confirming_bank_swift', value=confirming_swift)

























