import pandas as pd
from typing import Any, Optional
from datetime import date
from validators.base import BaseValidator
from config.validation_rules import DATE_RULES


class DateValidator(BaseValidator):
    """Validates LC dates and date relationships."""

    def _validate(self, field: str, value: Any, **context) -> None:
        # Phase 1: Check each date individually
        issue_date = self._check_single_date('issue_date', value)
        expiry_date = self._check_single_date('expiry_date', context.get('expiry_date'))
        shipment_date = self._check_single_date('latest_shipment_date', context.get('shipment_date'))

        # Phase 2: Cross-date checks (only if we have valid dates)
        self._check_date_sequences(issue_date, expiry_date, shipment_date)

    def _check_single_date(self, field: str, value: Any) -> Optional[
        date]:  # means this returns either a date object or None
        """Check one date: present, parseable, real. Returns parsed date or None."""

        ## Gate 1: Present?
        if value is None or pd.isna(value):
            self._add_error('DATE001', field=field, value=value)
            return None

        str_value = str(value).strip()
        if str_value == '':
            self._add_error('DATE001', field=field, value=value)
            return None

        ## Gate 2: Parseable as a date?
        try:
            parsed = date.fromisoformat(str_value)
        except ValueError:
            self._add_error('DATE002', field=field, value=str_value)
            return None

        ## Gate 3: Is it a real date? (Feb 30 passes format but isn't real)
        # fromisoformat() already rejects impossible dates, so DATE008 should
        # never trigger — this is a defensive safety net.
        try:
            date(parsed.year, parsed.month, parsed.day)
        except ValueError:
            self._add_error('DATE008', field=field, value=str_value)
            return None

        return parsed

    def _check_date_sequences(self, issue_date, expiry_date, shipment_date) -> None:
        """Phase 2: Compare dates against each other."""

        # Check 1: Expiry before issue? (DATE004)
        if issue_date and expiry_date:
            if expiry_date < issue_date:
                self._add_error('DATE004', field='expiry_date',
                                value=f'issue={issue_date} expiry={expiry_date}')

        # Check 2: Shipment after expiry? (DATE005)
        if shipment_date and expiry_date:
            if shipment_date > expiry_date:
                self._add_error('DATE005', field='latest_shipment_date',
                                value=f'shipment={shipment_date} expiry={expiry_date}')

        # Check 3: Validity period exceeds maximum? (DATE007)
        if issue_date and expiry_date:
            max_days = DATE_RULES['max_validity_days']
            validity= (expiry_date - issue_date).days #  subtracting two date objects gives a timedelta
            if validity > max_days:
                self._add_error('DATE007', field='expiry_date',
                                value=f'validity={validity} days (max={max_days})')























