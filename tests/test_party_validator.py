import pytest
from validators.party_validator import PartyValidator


@pytest.fixture
def validator():
    return PartyValidator()


def test_valid_party(validator):
    errors = validator.validate(
        field='applicant', value='Toyota Motor Corporation',
        address='1 Toyota-cho',
        country='JP',
        city='Toyota City',
        postal_code='471-8571'
    )
    assert len(errors) == 0


def test_pty001_name_missing(validator):
    errors = validator.validate(
        field='applicant', value=None,
        address='123 Main St',
        country='US',
        city='New York',
        postal_code='10001'
    )
    assert any(e.error_code == 'PTY001' for e in errors)


def test_pty002_name_too_short(validator):
    errors = validator.validate(
        field='applicant', value='A',
        address='123 Main St',
        country='US',
        city='New York',
        postal_code='10001'
    )
    assert any(e.error_code == 'PTY002' for e in errors)


def test_pty004_address_missing(validator):
    errors = validator.validate(
        field='applicant', value='Toyota Motor Corporation',
        address=None,
        country='JP',
        city='Tokyo',
        postal_code='100-0001'
    )
    assert any(e.error_code == 'PTY004' for e in errors)


def test_pty005_invalid_country(validator):
    errors = validator.validate(
        field='applicant', value='Fake Corp',
        address='123 Fake St',
        country='XX',
        city='Nowhere',
        postal_code='00000'
    )
    assert any(e.error_code == 'PTY005' for e in errors)


def test_pty010_city_missing(validator):
    errors = validator.validate(
        field='applicant', value='Toyota Motor Corporation',
        address='1 Toyota-cho',
        country='JP',
        city=None,
        postal_code='471-8571'
    )
    assert any(e.error_code == 'PTY010' for e in errors)