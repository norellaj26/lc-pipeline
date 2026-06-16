import pytest
from validators.lc_validator import LcValidator


@pytest.fixture
def validator():
    return LcValidator()


def test_valid_lc(validator):
    errors = validator.validate(
        field='lc_number', value='LC-2026-100',
        lc_form='IRREVOCABLE',
        available_with='BY PAYMENT',
        confirmation_status='UNCONFIRMED',
        confirming_bank_swift=None
    )
    assert len(errors) == 0


def test_lc001_missing(validator):
    errors = validator.validate(
        field='lc_number', value=None,
        lc_form='STANDBY',
        available_with='BY PAYMENT',
        confirmation_status='CONFIRMED',
        confirming_bank_swift='BARCGB22'
    )
    assert any(e.error_code == 'LC001' for e in errors)


def test_lc002_too_short(validator):
    errors = validator.validate(
        field='lc_number', value='LC',
        lc_form='STANDBY',
        available_with='BY PAYMENT',
        confirmation_status='UNCONFIRMED',
        confirming_bank_swift=None
    )
    assert any(e.error_code == 'LC002' for e in errors)


def test_lc004_invalid_form(validator):
    errors = validator.validate(
        field='lc_number', value='LC-2026-100',
        lc_form='INVALID_FORM',
        available_with='BY PAYMENT',
        confirmation_status='UNCONFIRMED',
        confirming_bank_swift=None
    )
    assert any(e.error_code == 'LC004' for e in errors)


def test_lc007_confirmed_no_bank(validator):
    errors = validator.validate(
        field='lc_number', value='LC-2026-100',
        lc_form='STANDBY',
        available_with='BY PAYMENT',
        confirmation_status='CONFIRMED',
        confirming_bank_swift=None
    )
    assert any(e.error_code == 'LC007' for e in errors)


def test_lc008_invalid_status(validator):
    errors = validator.validate(
        field='lc_number', value='LC-2026-100',
        lc_form='STANDBY',
        available_with='BY PAYMENT',
        confirmation_status='MAYBE',
        confirming_bank_swift=None
    )
    assert any(e.error_code == 'LC008' for e in errors)