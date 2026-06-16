import pandas as pd
from typing import Any
from validators.base import BaseValidator
from config.validation_rules import PARTY_RULES
from config.constants import VALID_COUNTRY_CODES, PATTERNS


class PartyValidator(BaseValidator):
    """Validates party fields (applicant/beneficiary)."""

    def _validate(self, field: str, value: Any, **context) -> None:
        # field = 'applicant' or 'beneficiary'
        # value = name (the most critical field)
        self._check_name(field, value)

        address = context.get('address')
        self._check_address(field, address)

        country = context.get('country')
        self._check_country(field, country)

        city = context.get('city')
        self._check_city(field, city)

        postal_code = context.get('postal_code')
        self._check_postal_code(field, postal_code)

    def _check_name(self, party: str, name: Any) -> None:
        """Check party name: present, length, characters."""
        field = f'{party}_name'

        # Gate 1: Present?
        if name is None or pd.isna(name):
            self._add_error('PTY001', field=field, value=name)
            return
        str_name = str(name).strip()
        if str_name == '':
            self._add_error('PTY001', field=field, value=name)
            return

        # Gate 2: Too short?
        min_len = PARTY_RULES['min_name_length']
        if len(str_name) < min_len:
            self._add_error('PTY002', field=field, value=str_name)

        # Gate 3: Too long?
        max_len = PARTY_RULES['max_name_length']
        if len(str_name) > max_len:
            self._add_error('PTY003', field=field, value=str_name)

    def _check_address(self, party: str, address: Any) -> None:
        """Check party address: present?"""
        field = f"{party}_address"

        # Gate 1: Present?
        if address is None or pd.isna(address):
            self._add_error('PTY004', field=field, value=address)
            return

        str_address = str(address).strip()
        if str_address == '':
            self._add_error('PTY004', field=field, value=address)
            return

        # Gate 2: Too short?
        min_len = PARTY_RULES['min_address_length']
        if len(str_address) < min_len:
            self._add_error('PTY008', field=field, value=str_address)

        # Gate 3: Too long?
        max_len = PARTY_RULES['max_address_length']
        if len(str_address) > max_len:
            self._add_error('PTY009', field=field, value=str_address)

    def _check_country(self, party: str, country: Any) -> None:
        """Check country code: valid ISO 3166?"""
        field = f'{party}_country'

        if country is None or pd.isna(country):
            self._add_error('PTY005', field=field, value=country)
            return

        # Normalize to uppercase before checking against ISO 3166-1 alpha-2 set
        str_country = str(country).strip().upper()
        if str_country not in VALID_COUNTRY_CODES:
            self._add_error('PTY005', field=field, value=str_country)

    def _check_city(self, party: str, city: Any) -> None:
        """Check party city: present and reasonable length?"""
        field = f'{party}_city'

        if city is None or pd.isna(city):
            self._add_error('PTY010', field=field, value=city)
            return

        str_city = str(city).strip()
        if str_city == '':
            self._add_error('PTY010', field=field, value=city)
            return

        min_len = PARTY_RULES['min_city_length']
        if len(str_city) < min_len:
            self._add_error('PTY011', field=field, value=str_city)

    def _check_postal_code(self, party: str, postal_code: Any) -> None:
        """Check postal code: present and valid format?"""
        field = f'{party}_postal_code'

        if postal_code is None or pd.isna(postal_code):
            self._add_error('PTY012', field=field, value=postal_code)
            return

        str_postal = str(postal_code).strip()
        if str_postal == '':
            self._add_error('PTY012', field=field, value=postal_code)
            return

        postal_pattern = PATTERNS['postal_code']
        if not postal_pattern.match(str_postal):
            self._add_error('PTY013', field=field, value=str_postal)