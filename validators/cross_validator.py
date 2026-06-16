import pandas as pd  # used for pd.isna() to catch NaN/None values
from typing import Any
from validators.base import BaseValidator  # parent class that provides _add_error()

class CrossValidator(BaseValidator):
    """Validates relationships between fields across the transaction."""

    def _validate(self, field: str, value: Any, **context) -> None:
        # field = 'transaction' (whole row)
        # value = transaction_id

        # It then delegates to two sub-checks
        self._check_same_party(value, context)
        self._check_bank_country(value, context)

    def _check_same_party(self, txn_id: str, context: dict) -> None:
        """XVAL001: Applicant and beneficiary can't be the same."""
        # Pulls both names from context
        app_name = context.get('applicant_name')
        ben_name= context.get('beneficiary_name')

        if not app_name or not ben_name:       # catches None / empty string
            return
        if pd.isna(app_name) or pd.isna(ben_name):  # catches float NaN from pandas
            return

        # Normalize before comparing so "ACME" == "acme " is caught
        if str(app_name).strip().upper() == str(ben_name).strip().upper():
            self._add_error('XVAL001', field='applicant_name',
                            value=f'applicant={app_name} beneficiary={ben_name}')

    def _check_bank_country(self, txn_id: str, context: dict) -> None:
        """XVAL002: Issuing bank country should match applicant country."""
        bank_country = context.get('issuing_bank_country')
        app_country = context.get('applicant_country')

        if not bank_country or not app_country:       # catches None / empty string
            return
        if pd.isna(bank_country) or pd.isna(app_country):  # catches float NaN from pandas
            return

        # Mismatch means the bank is in a different country than the applicant
        if str(bank_country).strip().upper() != str(app_country).strip().upper():
            self._add_error('XVAL002', field='issuing_bank_country',
                            value=f'bank={bank_country} applicant={app_country}')