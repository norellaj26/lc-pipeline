import pytest
from validators.cross_validator import CrossValidator


@pytest.fixture
def validator():
    return CrossValidator()


def test_valid_different_parties(validator):
    errors = validator.validate(
        field='transaction', value='LC-TEST01',
        applicant_name='Toyota Motor',
        beneficiary_name='Apple Inc',
        issuing_bank_country='JP',
        applicant_country='JP'
    )
    assert len(errors) == 0


def test_xval001_same_party(validator):
    errors = validator.validate(
        field='transaction', value='LC-TEST02',
        applicant_name='Toyota Motor',
        beneficiary_name='TOYOTA MOTOR',
        issuing_bank_country='JP',
        applicant_country='JP'
    )
    assert any(e.error_code == 'XVAL001' for e in errors)


def test_xval002_bank_country_mismatch(validator):
    errors = validator.validate(
        field='transaction', value='LC-TEST03',
        applicant_name='Toyota Motor',
        beneficiary_name='Apple Inc',
        issuing_bank_country='US',
        applicant_country='JP'
    )
    assert any(e.error_code == 'XVAL002' for e in errors)