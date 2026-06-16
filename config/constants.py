"""
constants.py
═══════════════════════════════════════════════════════════════════════════════
Static constants - values that DON'T change.
Currency definitions
Valid codes (incoterms, LC forms)
Regex patterns
Column names

For environment settings that CAN change, see settings.py
For validation rules and error codes, see validation_rules.py

Philosophy: NO hardcoded values anywhere else in the project!
═══════════════════════════════════════════════════════════════════════════════
"""
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Dict, Set, FrozenSet, List
import re

# Set       → Can be modified (add, remove)
# FrozenSet → Cannot be modified (immutable) ← Better for constants!


## 💱 CURRENCIES (ISO 4217)
# _ ═══════════════════════════════════════════════════════════════════════════════
#  Dict[str, Dict] means: Dictionary where keys are strings, values are dictionaries.
CURRENCY_INFO: Dict[str, Dict[str, Any]] = {
	'USD': {'decimals': 2, 'name': 'US Dollar', 'symbol': '$'},
	'EUR': {'decimals': 2, 'name': 'Euro', 'symbol': '€'},
	'GBP': {'decimals': 2, 'name': 'British Pound', 'symbol': '£'},
	'JPY': {'decimals': 0, 'name': 'Japanese Yen', 'symbol': '¥'},
	'CHF': {'decimals': 2, 'name': 'Swiss Franc', 'symbol': 'CHF'},
	'CAD': {'decimals': 2, 'name': 'Canadian Dollar', 'symbol': 'C$'},
	'AUD': {'decimals': 2, 'name': 'Australian Dollar', 'symbol': 'A$'},
	'CNY': {'decimals': 2, 'name': 'Chinese Yuan', 'symbol': '¥'},
	'KRW': {'decimals': 0, 'name': 'Korean Won', 'symbol': '₩'},
	'TWD': {'decimals': 2, 'name': 'Taiwan Dollar', 'symbol': 'NT$'},
}

VALID_CURRENCIES: FrozenSet[str] = frozenset(CURRENCY_INFO.keys())
# → dict_keys(['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY', 'KRW', 'TWD'])
# FrozenSet[str] makes it immutable (cannot be changed at runtime)


## 🏛️ MT700 FIELD DEFINITIONS (SWIFT Letter of Credit)
# _ ═══════════════════════════════════════════════════════════════════════════════

LC_FORMS: FrozenSet[str] = frozenset({
	'IRREVOCABLE',
	'IRREVOCABLE TRANSFERABLE',
	'STANDBY',
})
# [str] -> Type hint — tells type checkers what's inside
AVAILABLE_WITH_OPTIONS: FrozenSet[str] = frozenset({
	'BY PAYMENT',
	"BY ACCEPTANCE",
	'BY NEGOTIATION',
	'BY DEFERRED PAYMENT',
	'BY MIXED PAYMENT',
})

CONFIRMATION_STATUSES: FrozenSet[str] = frozenset({
	'CONFIRMED',
	'UNCONFIRMED',
})


## 🚢 INCOTERMS (International Commercial Terms 2020)
# _ ═══════════════════════════════════════════════════════════════════════════════

INCOTERMS_ANY_MODE: FrozenSet[str] = frozenset({
	'EXW', # Ex Works
	'FCA', # Free Carrier
	'CPT', # Carriage Paid To
	'CIP', # Carriage and Insurance Paid To
	'DAP', # Delivered at Place
	'DPU', # Delivered at Place Unloaded
	'DDP'  # Delivered Duty Paid  -> Buyer's door
})

INCOTERMS_SEA_ONLY: FrozenSet[str] = frozenset({
	'FAS', # Free Alongside Ship
	'FOB', # Free On Board
	'CFR', # Cost and Freight
	'CIF', # Cost, Insurance and Freight
})

# Combines both sets into one! Give me elements in set_a OR set_b
INCOTERMS_ALL: FrozenSet[str] = INCOTERMS_ANY_MODE | INCOTERMS_SEA_ONLY

PARTIAL_SHIPMENT_OPTIONS: FrozenSet[str] = frozenset({
    'ALLOWED',
    'NOT ALLOWED',
})

## 🔤 REGEX PATTERNS (Compiled for performance!)
# _ ═══════════════════════════════════════════════════════════════════════════════

PATTERNS: Dict[str, re.Pattern] = {
	'Lei': re.compile(r'^[A-Z0-9]{18}[0-9]{2}$'),
	'swift_bic': re.compile(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$'),
	'country_code': re.compile(r'^[A-Z]{2}$'),
	'port_code': re.compile(r'^[A-Z]{2}[A-Z0-9]{3}$'),
	'postal_code': re.compile(r'^[A-Z0-9\s\-]{3,10}$', re.IGNORECASE),
	'date-iso': re.compile(r'^\d{4}-\d{2}-\d{2}$')
}

## 🔤 UNICODE NORMALIZATION
# _ ═══════════════════════════════════════════════════════════════════════════════

UNICODE_REPLACEMENTS: Dict[str, str] = {
    # Dashes → standard hyphen
    '\u2010': '-',  # Hyphen
    '\u2011': '-',  # Non-breaking hyphen
    '\u2012': '-',  # Figure dash
    '\u2013': '-',  # En-dash
    '\u2014': '-',  # Em-dash
    '\u2015': '-',  # Horizontal bar
    '\u2212': '-',  # Minus sign
    # Quotes → standard quote
    '\u201C': '"',  # Left double quote "
    '\u201D': '"',  # Right double quote "
    '\u2018': "'",  # Left single quote '
    '\u2019': "'",  # Right single quote '
    # Spaces → standard space
    '\u00A0': ' ',  # Non-breaking space
    '\u2009': ' ',  # Thin space
    '\u200B': '',   # Zero-width space (remove!)
}


## 📋 COLUMN DEFINITIONS (44 columns from dataset)
# _ ═══════════════════════════════════════════════════════════════════════════════

COLS_CORE: list[str] = [
	'transaction_id',
	'lc_number',
	'lc_form',
	'available_with'
]

COLS_DATES: List[str] = [
	'issue_date',
	'expiry_date',
	'latest_shipment_date'
]

COLS_APPLICANT: List[str] = [
	'applicant_name',
	'applicant_address',
	'applicant_city',
	'applicant_postal_code',
	'applicant_country',
	'applicant_lei',
	'applicant_account',
]

COLS_BENEFICIARY: List[str] = [
	'beneficiary_name',
	'beneficiary_address',
	'beneficiary_city',
	'beneficiary_postal_code',
	'beneficiary_country',
	'beneficiary_lei',
	'beneficiary_account',
]

COLS_BANKS: List[str] = [
	'issuing_bank_name',
	'issuing_bank_swift',
	'issuing_bank_country',
	'advising_bank_name',
	'advising_bank_swift',
	'confirming_bank_name',
	'confirming_bank_swift',
	'confirmation_status',
]

COLS_AMOUNT: List[str] = [
	'amount',
	'currency',
	'tolerance_percent'
]

COLS_SHIPMENT: list[str] = [
	'partial_shipment',
	'transhipment_allowed',
	'incoterm',
	'port_of_loading',
	'port_of_discharge',
	'vessel_name'
]

COLS_DOCUMENTS: list[str] = [
	'goods_description',
	'documents_required',
	'additional_conditions',
	'presentation_period_days',
]

COLS_PAYMENT: List[str] = [
	'payment_terms',
	'charges'
]

## All input columns combined

COLS_ALL_INPUT: List[str] = (
    COLS_CORE +
    COLS_DATES +
    COLS_APPLICANT +
    COLS_BENEFICIARY +
    COLS_BANKS +
    COLS_AMOUNT +
    COLS_SHIPMENT +
    COLS_DOCUMENTS +
    COLS_PAYMENT
)

## Columns added during validation

COLS_VALIDATION: List[str] = [
	'validation_status',
	'error_count',
	'error_codes',
	'error_messages',
	'severity'
]

## 🎯 SEVERITY LEVELS
# _ ═══════════════════════════════════════════════════════════════════════════════
class Severity:
    """Validation error severity levels"""
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    NONE = 'NONE'


SEVERITY_ORDER: Dict[str, int] = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
    Severity.NONE: 0,
}

## 🎨 SEVERITY COLORS (RAG Palette)
# _ ═══════════════════════════════════════════════════════════════════════════════
# Color mapping for severity levels — used in charts, dashboards, alerts.
# Keys reference the Severity class (single source of truth for severity strings).
# Hex codes follow universal RAG convention (Red/Amber/Green) for compliance dashboards.

SEVERITY_COLORS: Dict[str, str] = {
    Severity.CRITICAL: '#8B0000',  # Dark red — "stop the world"
    Severity.HIGH:     '#DC143C',  # Crimson — "pay attention now"
    Severity.MEDIUM:   '#FFA500',  # Orange — "review soon"
    Severity.LOW:      '#FFD700',  # Gold — "note for cleanup"
    Severity.NONE:     '#28A745',  # Green — "all good"
}


## 🎨 PROJECT PALETTE (Visual Identity)
# _ ═══════════════════════════════════════════════════════════════════════════════
# Full palette for charts: severity colors + status aliases + structural colors.
# Severity entries REFERENCE SEVERITY_COLORS — single source of truth for hex values.
# 'flagged'/'clean' are semantic aliases for the most common status colors,
# so chart code reads like English: PIPELINE_PALETTE['flagged'] for the flagged slice.
# 'primary'/'secondary'/'accent' are structural colors (titles, gridlines, highlights).

PIPELINE_PALETTE: Dict[str, str] = {
    # Severity — borrowed from SEVERITY_COLORS (DRY principle)
    'critical':   SEVERITY_COLORS[Severity.CRITICAL],
    'high':       SEVERITY_COLORS[Severity.HIGH],
    'medium':     SEVERITY_COLORS[Severity.MEDIUM],
    'low':        SEVERITY_COLORS[Severity.LOW],
    'none':       SEVERITY_COLORS[Severity.NONE],
    # Status — semantic aliases (alias = different name, same color)
    'flagged':    SEVERITY_COLORS[Severity.HIGH],   # = #DC143C
    'clean':      SEVERITY_COLORS[Severity.NONE],   # = #28A745
    # Structural — for titles, gridlines, accents (NOT severity-related)
    'primary':    '#1F4E79',  # Deep banking blue
    'secondary':  '#7F7F7F',  # Gray
    'accent':     '#5B9BD5',  # Light blue
}

## 🌍 COUNTRY CODES (ISO 3166-1 alpha-2)
# _ ═══════════════════════════════════════════════════════════════════════════════

VALID_COUNTRY_CODES: FrozenSet[str] = frozenset({
    # North America
    'US', 'CA', 'MX',
    # Europe
    'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'CH', 'AT', 'SE', 'NO', 'DK', 'FI',
    # Asia Pacific
    'JP', 'CN', 'KR', 'TW', 'HK', 'SG', 'AU', 'NZ', 'IN', 'TH', 'MY', 'ID', 'PH',
    # Middle East
    'AE', 'SA', 'IL', 'TR',
    # Latin America
    'BR', 'AR', 'CL', 'CO', 'PE',
    # Africa
    'ZA', 'EG', 'NG', 'KE',
})

## 🌍 UPPERCASE COLUMNS
# _ ═══════════════════════════════════════════════════════════════════════════════

COLS_UPPERCASE: List[str] = [
    # Compared against frozen sets
    'currency',
    'lc_form',
    'available_with',
    'confirmation_status',
    'incoterm',
    'applicant_country',
    'beneficiary_country',
    'issuing_bank_country',
    # Code fields (uppercase by spec)
    'issuing_bank_swift',
    'advising_bank_swift',
    'confirming_bank_swift',
    'applicant_lei',
    'beneficiary_lei',
    'port_of_loading',
    'port_of_discharge',
    # Categorical fields
    'partial_shipment',
    'transhipment_allowed',
    'charges',
]


















