import pytest
from validators.amount_validator import AmountValidator

@pytest.fixture()
def validator():
    return AmountValidator()
   ## Partial test
   # pytest tests/test_amount_validator.py -v
   ## entire test
   # pytest tests/ -v

# Pytest sees validator and injects a fresh AmountValidator() automatically.
def test_valid_amount(validator):
    errors = validator.validate(field='amount', value='1000.00', currency='USD')
    assert len(errors) == 0

def test_valid_amount_with_commas(validator):
    errors = validator.validate(field='amount', value='1,000,000.00', currency='EUR')
    assert len(errors) == 0

def test_amt001_zero(validator):
    errors = validator.validate(field='amount', value='0', currency='USD')
    assert len(errors) == 1
    assert errors[0].error_code == 'AMT001'


def test_amt002_negative(validator):
    errors = validator.validate(field='amount', value='-5000', currency='USD')
    assert len(errors) == 1
    assert errors[0].error_code == 'AMT002'


def test_amt005_invalid_format(validator):
    errors = validator.validate(field='amount', value='INVALID', currency='USD')
    assert len(errors) == 1
    assert errors[0].error_code == 'AMT005'


def test_amt005_malformed_commas(validator):
    errors = validator.validate(field='amount', value='22,43,565', currency='USD')
    assert len(errors) == 1
    assert errors[0].error_code == 'AMT005'

def test_amt003_exceeds_maximum(validator):
    errors = validator.validate(field='amount', value='9999999999.99', currency='USD')
    assert any(e.error_code == 'AMT003' for e in errors)

def test_amt006_wrong_decimals_for_jpy(validator):
    errors = validator.validate(field='amount', value='1000.50', currency='JPY')
    assert any(e.error_code == 'AMT006' for e in errors)

def test_amt005_none_value(validator):
    errors = validator.validate(field='amount', value=None, currency='USD')
    assert len(errors) == 1
    assert errors[0].error_code == 'AMT005'
