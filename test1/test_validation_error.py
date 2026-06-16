# test_validation_error.py (in your project root)
from models.validation_error import ValidationError
from dataclasses import FrozenInstanceError

# Test 1: Manual creation
err1 = ValidationError(
    error_code='AMT001',
    message='Amount zero',
    severity='CRITICAL',
    field='amount',
    value='0'
)
print("=== Test 1: Manual ===")
print(err1)
print(repr(err1))

# Test 2: Factory method
err2 = ValidationError.from_code('AMT005', field='amount', value='22,43,565')
print("\n=== Test 2: Factory ===")
print(err2)

# Test 3: to_dict
print("\n=== Test 3: Dict ===")
print(err2.to_dict())

# Test 4: Frozen — this should CRASH
print("\n=== Test 4: Frozen ===")
try:
    err2.severity = 'LOW'
except FrozenInstanceError as e:
    print(f"Blocked! Cannot modify: {e}")

