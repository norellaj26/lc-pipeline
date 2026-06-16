import pytest
from validators.shipment_validator import ShipmentValidator


@pytest.fixture
def validator():
    return ShipmentValidator()


def test_valid_shipment(validator):
    errors = validator.validate(
        field='incoterm', value='CIF',
        port_of_loading='DEHAM',
        port_of_discharge='USSFO',
        partial_shipment='ALLOWED'
    )
    assert len(errors) == 0


def test_ship001_invalid_incoterm(validator):
    errors = validator.validate(
        field='incoterm', value='XXX',
        port_of_loading='DEHAM',
        port_of_discharge='USSFO',
        partial_shipment='ALLOWED'
    )
    assert any(e.error_code == 'SHIP001' for e in errors)


def test_ship002_loading_missing(validator):
    errors = validator.validate(
        field='incoterm', value='FCA',
        port_of_loading=None,
        port_of_discharge='USSFO',
        partial_shipment='ALLOWED'
    )
    assert any(e.error_code == 'SHIP002' for e in errors)


def test_ship003_discharge_missing(validator):
    errors = validator.validate(
        field='incoterm', value='FCA',
        port_of_loading='DEHAM',
        port_of_discharge=None,
        partial_shipment='ALLOWED'
    )
    assert any(e.error_code == 'SHIP003' for e in errors)


def test_ship005_sea_incoterm_no_port(validator):
    errors = validator.validate(
        field='incoterm', value='FOB',
        port_of_loading=None,
        port_of_discharge='USSFO',
        partial_shipment='ALLOWED'
    )
    assert any(e.error_code == 'SHIP005' for e in errors)


def test_ship006_invalid_partial(validator):
    errors = validator.validate(
        field='incoterm', value='DAP',
        port_of_loading='DEHAM',
        port_of_discharge='USSFO',
        partial_shipment='MAYBE'
    )
    assert any(e.error_code == 'SHIP006' for e in errors)