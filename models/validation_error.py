from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationError:
    error_code: str
    message: str
    severity: str
    field: str
    value: Any

    @classmethod # it receives the class itself (cls) as the first argument instead of an instance (self)
    def from_code(cls, error_code: str, field: str, value: Any) -> 'ValidationError':
        from config.validation_rules import get_error_message, get_error_severity

        return cls(
            error_code=error_code,
            message=get_error_message(error_code),
            severity=get_error_severity(error_code),
            field=field,
            value=value,

        )
    # err = ValidationError.from_code('AMT005', field='amount', value='22,43,565')
    def __str__(self)->str:
        return f"[{self.severity}] {self.error_code}: {self.field} - {self.message} (got: {self.value})"
    # print(err)
    # [CRITICAL] AMT005: amount — Invalid amount format (got: 22,43,565)

    def to_dict(self) -> dict:
        return {
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity,
            'field': self.field,
            'value': self.value,
        }

