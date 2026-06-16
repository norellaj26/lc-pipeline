import pytest
from validators.date_validator import DateValidator


@pytest.fixture
def validator():
    return DateValidator()


def test_valid_dates(validator):
    errors = validator.validate(
        field='issue_date', value='2026-01-15',
        expiry_date='2026-06-15',
        shipment_date='2026-05-15'
    )
    assert len(errors) == 0


def test_date001_missing(validator):
    errors = validator.validate(
        field='issue_date', value=None,
        expiry_date='2026-06-15',
        shipment_date='2026-05-15'
    )
    assert any(e.error_code == 'DATE001' for e in errors)


def test_date002_invalid_format(validator):
    errors = validator.validate(
        field='issue_date', value='2026-02-30',
        expiry_date='2026-06-15',
        shipment_date='2026-05-15'
    )
    assert any(e.error_code == 'DATE002' for e in errors)


def test_date004_expiry_before_issue(validator):
    errors = validator.validate(
        field='issue_date', value='2026-06-01',
        expiry_date='2026-03-01',
        shipment_date='2026-02-15'
    )
    assert any(e.error_code == 'DATE004' for e in errors)


def test_date005_shipment_after_expiry(validator):
    errors = validator.validate(
        field='issue_date', value='2026-01-15',
        expiry_date='2026-06-15',
        shipment_date='2026-08-20'
    )
    assert any(e.error_code == 'DATE005' for e in errors)


def test_date007_validity_exceeds_max(validator):
    errors = validator.validate(
        field='issue_date', value='2026-01-10',
        expiry_date='2028-06-10',
        shipment_date='2026-05-15'
    )
    assert any(e.error_code == 'DATE007' for e in errors)