from validators.base import BaseValidator
from models.validation_error import ValidationError
from typing import List


# Test 1: Can't create BaseValidator directly
print("=== Test 1: ABC Protection ===")
try:
    base = BaseValidator()
except TypeError as e:
    print(f"Blocked! {e}")


# Test 2: Create a tiny child validator
class DummyValidator(BaseValidator):
    def _validate(self, field: str, value, **context) -> None:
        if value is None:
            self._add_error('AMT001', field=field, value=value)
        if value == 0:
            self._add_error('AMT001', field=field, value=value)


validator = DummyValidator()

print("\n=== Test 2: No errors ===")
errors = validator.validate('amount', 1000)
print(f"Errors: {len(errors)}")
print(f"has_errors: {validator.has_errors}")

print("\n=== Test 3: With errors ===")
errors = validator.validate('amount', 0)
print(f"Errors: {len(errors)}")
for err in errors:
    print(err)

print("\n=== Test 4: Defensive copy ===")
errors = validator.errors
errors.clear()
print(f"Cleared copy: {len(errors)}")
print(f"Original safe: {len(validator.errors)}")