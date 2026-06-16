"""
validation_rules.py
═══════════════════════════════════════════════════════════════════════════════
VALIDATION RULES - SINGLE SOURCE OF TRUTH

ALL validation logic is defined HERE. Validators READ from this file.
NO hardcoded values in validators!

Error Code Format: XXX000
- AMT = Amount
- LEI = Legal Entity Identifier
- BIC = SWIFT/BIC Code
- DATE = Date validation
- PTY = Party (applicant/beneficiary)
- LC = Letter of Credit specific
- SHIP = Shipment
- XVAL = Cross-validation (between documents)
═══════════════════════════════════════════════════════════════════════════════
"""
from decimal import Decimal
from typing import Dict, TypedDict, List
from .constants import Severity
from datetime import date, timedelta



# * 📝 TYPE DEFINITIONS FOR AMOUNT VALIDATION

class ErrorInfo(TypedDict):
    message: str
    severity: str


class AmountRulesType(TypedDict):
    min_value: Decimal
    max_value: Decimal
    allow_zero: bool
    allow_negative: bool
    errors: Dict[str, ErrorInfo]


# -💰 AMOUNT VALIDATION
# _ ═══════════════════════════════════════════════════════════════════════════════

AMOUNT_RULES: AmountRulesType = {
    'min_value': Decimal('1000.00'),  # UCP 600: op costs $500-$2000, no real LC below $1000
    'max_value': Decimal('999999999.99'),
    'allow_zero': False,
    'allow_negative': False,
    'errors': {
        'AMT001': {'message': 'Amount zero', 'severity': Severity.CRITICAL},
        'AMT002': {'message': 'Amount negative', 'severity': Severity.CRITICAL},
        'AMT003': {'message': 'Amount exceeds maximum allowed', 'severity': Severity.HIGH},
        'AMT004': {'message': 'Amount below minimum allowed', 'severity': Severity.HIGH},
        'AMT005': {'message': 'Invalid amount format', 'severity': Severity.CRITICAL},
        'AMT006': {'message': 'Wrong decimal places for currency', 'severity': Severity.MEDIUM},
    },

}


# * 📝 TYPE DEFINITIONS FOR LEI VALIDATION

class LeiRulesType(TypedDict):
    length: int
    require_api_validation: bool
    errors: Dict[str, ErrorInfo]


# - 🔖 LEI VALIDATION
# _ ═══════════════════════════════════════════════════════════════════════════════

LEI_RULES: LeiRulesType = {
    'length': 20,
    'require_api_validation': True,
    'errors': {
        'LEI001': {'message': 'LEI empty or missing', 'severity': Severity.HIGH},
        'LEI002': {'message': 'LEI invalid length (must be 20)', 'severity': Severity.HIGH},
        'LEI003': {'message': 'LEI invalid format', 'severity': Severity.HIGH},
        'LEI004': {'message': 'LEI not found in GLEIF.md database', 'severity': Severity.HIGH},
        'LEI005': {'message': 'LEI inactive/lapsed in GLEIF.md', 'severity': Severity.MEDIUM},
        'LEI006': {'message': 'GLEIF.md API error - could not validate', 'severity': Severity.LOW},
    },
    # LEI001-003 = format checks (no API needed)
    # LEI004-006 = API checks (call GLEIF.md)
}


# * 📝 TYPE DEFINITIONS FOR SWIFT VALIDATION

class SwiftRulesType(TypedDict):
    valid_lengths: List[int]
    errors: Dict[str, ErrorInfo]


# - 🏦 SWIFT/BIC VALIDATION
# _ ═══════════════════════════════════════════════════════════════════════════════
SWIFT_RULES: SwiftRulesType = {
    'valid_lengths': [8, 11],
    'errors': {
        'BIC001': {'message': 'SWIFT/BIC empty or missing', 'severity': Severity.HIGH},
        'BIC002': {'message': 'SWIFT/BIC invalid length (must be 8 or 11)', 'severity': Severity.HIGH},
        'BIC003': {'message': 'SWIFT/BIC invalid format', 'severity': Severity.HIGH},
        'BIC004': {'message': 'SWIFT/BIC country code mismatch', 'severity': Severity.MEDIUM},

    },
}


# * 📝 TYPE DEFINITIONS FOR DATE VALIDATION

class DateRulesType(TypedDict):
    min_date: str
    max_date: str
    max_validity_days: int
    max_future_issue_days: int
    errors: Dict[str, ErrorInfo]


# - 📅 DATE VALIDATION
# _ ═══════════════════════════════════════════════════════════════════════════════
_today = date.today()
_max_validity = 540
_max_future_issue = 30

DATE_RULES: DateRulesType = {
    'min_date': (_today - timedelta(days=_max_validity)).isoformat(),
    'max_date': (_today + timedelta(days=_max_validity + _max_future_issue)).isoformat(),
    'max_validity_days': _max_validity,
    'max_future_issue_days': _max_future_issue,
    'errors': {
        'DATE001': {'message': 'Date empty or missing', 'severity': Severity.HIGH},
        'DATE002': {'message': 'Date invalid format', 'severity': Severity.HIGH},
        'DATE003': {'message': 'Date out of valid range', 'severity': Severity.MEDIUM},
        'DATE004': {'message': 'Expiry date before issue date', 'severity': Severity.CRITICAL},
        'DATE005': {'message': 'Shipment date after expiry date', 'severity': Severity.CRITICAL},
        'DATE006': {'message': 'Issue date too far in future', 'severity': Severity.MEDIUM},
        'DATE007': {'message': 'LC validity period exceeds maximum', 'severity': Severity.MEDIUM},
        'DATE008': {'message': 'Invalid day/month combination', 'severity': Severity.HIGH},
    },

}


# * 📝 TYPE DEFINITIONS FOR PARTY VALIDATION

class PartyRulesType(TypedDict):
    min_name_length: int
    max_name_length: int
    min_address_length: int
    max_address_length: int
    min_city_length: int
    require_address: bool
    require_lei: bool
    errors: Dict[str, ErrorInfo]


# - 👥 PARTY VALIDATION (Applicant & Beneficiary)
# _ ═══════════════════════════════════════════════════════════════════════════════
PARTY_RULES: PartyRulesType = {
    'min_name_length': 2,
    'max_name_length': 140,
    'min_address_length': 5,
    'max_address_length': 200,
    'min_city_length': 2,
    'require_address': True,
    'require_lei': True,
    'errors': {
        'PTY001': {'message': 'Party name empty or missing', 'severity': Severity.CRITICAL},
        'PTY002': {'message': 'Party name too short', 'severity': Severity.HIGH},
        'PTY003': {'message': 'Party name too long', 'severity': Severity.MEDIUM},
        'PTY004': {'message': 'Party address empty or missing', 'severity': Severity.HIGH},
        'PTY005': {'message': 'Party country code invalid', 'severity': Severity.HIGH},
        'PTY006': {'message': 'Party LEI missing', 'severity': Severity.HIGH},
        'PTY007': {'message': 'Party name contains invalid characters', 'severity': Severity.MEDIUM},
        'PTY008': {'message': 'Party address too short', 'severity': Severity.MEDIUM},
        'PTY009': {'message': 'Party address too long', 'severity': Severity.MEDIUM},
        'PTY010': {'message': 'Party city empty or missing', 'severity': Severity.HIGH},
        'PTY011': {'message': 'Party city too short', 'severity': Severity.MEDIUM},
        'PTY012': {'message': 'Party postal code empty or missing', 'severity': Severity.MEDIUM},
        'PTY013': {'message': 'Party postal code invalid format', 'severity': Severity.MEDIUM},
    },
}


# * 📝 TYPE DEFINITIONS FOR LC VALIDATION
class LcRulesType(TypedDict):
    lc_number_min_length: int
    lc_number_max_length: int
    require_confirming_bank: bool
    errors: Dict[str, ErrorInfo]


# - 📜 LETTER OF CREDIT VALIDATION
# _  ═══════════════════════════════════════════════════════════════════════════════
LC_RULES: LcRulesType = {
    'lc_number_min_length': 5,
    'lc_number_max_length': 35,
    'require_confirming_bank': False,
    'errors': {
        'LC001': {'message': 'LC number empty or missing', 'severity': Severity.CRITICAL},
        'LC002': {'message': 'LC number too short', 'severity': Severity.CRITICAL},
        'LC003': {'message': 'LC number too long', 'severity': Severity.CRITICAL},
        'LC004': {'message': 'Invalid LC form type', 'severity': Severity.CRITICAL},
        'LC005': {'message': 'Invalid available with option', 'severity': Severity.CRITICAL},
        'LC006': {'message': 'Issuing bank SWIFT missing', 'severity': Severity.CRITICAL},
        'LC007': {'message': 'Confirming bank required but missing', 'severity': Severity.CRITICAL},
        'LC008': {'message': 'Confirmation status invalid', 'severity': Severity.CRITICAL},
    },
}


# * 📝 TYPE DEFINITIONS FOR SHIPMENT VALIDATION

class ShipmentRulesType(TypedDict):
    require_port_of_loading: bool
    require_port_of_discharge: bool
    errors: Dict[str, ErrorInfo]


# -  🚢 SHIPMENT VALIDATION
# _ ═══════════════════════════════════════════════════════════════════════════════
SHIPMENT_RULES: ShipmentRulesType = {
    'require_port_of_loading': True,
    'require_port_of_discharge': True,
    'errors': {
        'SHIP001': {'message': 'Invalid incoterm', 'severity': Severity.HIGH},
        'SHIP002': {'message': 'Port of loading missing', 'severity': Severity.HIGH},
        'SHIP003': {'message': 'Port of discharge missing', 'severity': Severity.HIGH},
        'SHIP004': {'message': 'Invalid port code format', 'severity': Severity.MEDIUM},
        'SHIP005': {'message': 'Sea incoterm used but no port specified', 'severity': Severity.HIGH},
        'SHIP006': {'message': 'Partial shipment value invalid', 'severity': Severity.LOW},
    },
}


# * 📝 TYPE DEFINITIONS FOR Cross-Validation VALIDATION
class CrossValidationRulesType(TypedDict):
    errors: Dict[str, ErrorInfo]


# - 🔗 CROSS-VALIDATION (Between fields/documents)
# _ ═══════════════════════════════════════════════════════════════════════════════

CROSS_VALIDATION_RULES: CrossValidationRulesType = {
    'errors': {
        'XVAL001': {'message': 'Applicant and beneficiary are the same party', 'severity': Severity.HIGH},
        'XVAL002': {'message': 'Issuing bank country does not match applicant country', 'severity': Severity.MEDIUM},
        # XVAL003: Reserved (currency/bank validation - requires external data)
        'XVAL004': {'message': 'Shipment date outside LC validity period', 'severity': Severity.CRITICAL},
    },
}

# - 📚 ALL ERROR CODES (Auto-built from all rules)
# _  ═══════════════════════════════════════════════════════════════════════════════

ALL_ERROR_CODES: Dict[str, ErrorInfo] = {
    **AMOUNT_RULES['errors'],
    **LEI_RULES['errors'],
    **SWIFT_RULES['errors'],
    **DATE_RULES['errors'],
    **PARTY_RULES['errors'],
    **LC_RULES['errors'],
    **SHIPMENT_RULES['errors'],
    **CROSS_VALIDATION_RULES['errors'],

}


def get_error_info(error_code: str) -> ErrorInfo | None:
    """
        Get error info by code.

        Args:
            error_code: Error code like 'AMT001', 'LEI002'

        Returns:
            ErrorInfo dict with message and severity, or None if not found

        Example:
             -> get_error_info('AMT001')
            {'message': 'Amount is zero', 'severity': 'CRITICAL'}
    """
    return ALL_ERROR_CODES.get(error_code)


def get_error_message(error_code: str) -> str:
    """Get just the message for an error code."""
    info = get_error_info(error_code)
    return info['message'] if info else f'Unknown error: {error_code}'

def get_error_severity(error_code: str) -> str:
    """Get just the severity for an error code."""
    info = get_error_info(error_code)
    return info['severity'] if info else Severity.MEDIUM
