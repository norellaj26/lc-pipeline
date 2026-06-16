import pytest
from validators.swift_validator import SwiftValidator


@pytest.fixture
def validator():
    return SwiftValidator()


def test_valid_swift_8_chars(validator):
    errors = validator.validate(field='issuing_bank_swift', value='SMBCJPJT')
    assert len(errors) == 0


def test_valid_swift_11_chars(validator):
    errors = validator.validate(field='issuing_bank_swift', value='SMBCJPJTXXX')
    assert len(errors) == 0


def test_bic001_missing(validator):
    errors = validator.validate(field='issuing_bank_swift', value=None)
    assert len(errors) == 1
    assert errors[0].error_code == 'BIC001'


def test_bic002_wrong_length(validator):
    errors = validator.validate(field='issuing_bank_swift', value='SHORT')
    assert len(errors) == 1
    assert errors[0].error_code == 'BIC002'


def test_bic003_invalid_format(validator):
    errors = validator.validate(field='issuing_bank_swift', value='12345678')
    assert len(errors) == 1
    assert errors[0].error_code == 'BIC003'