import pytest
from validators.lei_validator import LeiValidator


@pytest.fixture
def validator():
    return LeiValidator()


def test_valid_lei_active(validator):
    """Real Apple LEI — should pass all gates including API."""
    errors = validator.validate(field='applicant_lei', value='HWUPKR0MPOU8FGXBT394')
    assert len(errors) == 0


def test_lei001_missing(validator):
    errors = validator.validate(field='applicant_lei', value=None)
    assert len(errors) == 1
    assert errors[0].error_code == 'LEI001'


def test_lei002_wrong_length(validator):
    errors = validator.validate(field='applicant_lei', value='TOOSHORT123')
    assert len(errors) == 1
    assert errors[0].error_code == 'LEI002'


def test_lei003_invalid_format(validator):
    errors = validator.validate(field='applicant_lei', value='INVALID!!LEI##CODE99')
    assert len(errors) == 1
    assert errors[0].error_code == 'LEI003'


def test_lei004_not_in_gleif(validator):
    """Valid format but fake — API returns NOT_FOUND."""
    errors = validator.validate(field='applicant_lei', value='AAAABBBBCCCCDDDD0000')
    assert len(errors) == 1
    assert errors[0].error_code == 'LEI004'