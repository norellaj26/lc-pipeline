import pandas as pd
from typing import Any
from validators.base import BaseValidator
from config.validation_rules import SHIPMENT_RULES
from config.constants import (
    INCOTERMS_ALL, INCOTERMS_SEA_ONLY,
    PATTERNS, PARTIAL_SHIPMENT_OPTIONS
)

class ShipmentValidator(BaseValidator):
    """Validates shipment fields."""

    def _validate(self, field: str, value: Any, **context) -> None:
        # value = incoterm (the primary field)
        self._check_incoterm(field, value)

        port_of_loading = context.get('port_of_loading')
        self._check_port('port_of_loading', port_of_loading)

        port_of_discharge = context.get('port_of_discharge')
        self._check_port('port_of_discharge', port_of_discharge)

        # Sea incoterms need ports
        self._check_sea_incoterm_ports(value, port_of_loading, port_of_discharge)
        #  mini cross-check within shipment. FOB/CIF/etc. are meaningless without ports.

        partial_shipment = context.get('partial_shipment')
        self._check_partial_shipment(partial_shipment)

    def _check_incoterm(self, field: str, value: Any) -> None:
        """Check incoterm against valid options."""

        if value is None or pd.isna(value):
            self._add_error('SHIP001', field=field, value=value)
            return

        str_value = str(value).strip()
        if str_value not in INCOTERMS_ALL:
            self._add_error('SHIP001', field=field, value=str_value)

    #  The else is just a code-picker
    #  inside a single call, not a blocker between the two calls.
    # 2 calls from _validate
    def _check_port(self, field: str, value: Any) -> None:
        """Check port: present and valid format."""

        if value is None or pd.isna(value):
           if field == 'port_of_loading':
               self._add_error('SHIP002', field=field, value=value)
           else:
               self._add_error('SHIP003', field=field, value=value)
           return

        str_value = str(value).strip()
        if str_value == '':
            if field == 'port_of_loading':
                self._add_error('SHIP002', field=field, value=value)
            else:
                self._add_error('SHIP003', field=field, value=value)
            return

        # Format check against port code pattern
        port_pattern = PATTERNS['port_code']
        if not port_pattern.match(str_value):
            self._add_error('SHIP004', field=field, value=str_value)

    def _check_sea_incoterm_ports(self, incoterm: Any, loading: Any, discharge: Any) -> None:
        """Sea incoterms require both ports."""

        if incoterm is None or pd.isna(incoterm):
            return

        str_incoterm = str(incoterm).strip()
        if str_incoterm not in INCOTERMS_SEA_ONLY:
            return

        # It's a sea incoterm — ports are mandatory
        if loading is None or pd.isna(loading):
            self._add_error('SHIP005', field='port_of_loading',
                            value=f'sea incoterm {str_incoterm} requires port')

        if discharge is None or pd.isna(discharge):
                self._add_error('SHIP005', field='port_of_discharge',
                            value=f'sea incoterm {str_incoterm} requires port ')


    def _check_partial_shipment(self, value: Any) -> None:
        """Check partial shipment has valid value."""

        if value is None or pd.isna(value):
            return # Optional field

        str_value = str(value).strip()
        if str_value not in PARTIAL_SHIPMENT_OPTIONS:
            self._add_error('SHIP006', field='partial_shipment', value=str_value)




















