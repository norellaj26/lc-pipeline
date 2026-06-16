from abc import ABC, abstractmethod
from typing import List
from models.validation_error import ValidationError


class BaseValidator(ABC):
    """Base class for all validators in the pipeline."""

    def __init__(self) -> None:
        self._errors: List[ValidationError] = []

    def validate(self, field: str, value, **context) -> List[ValidationError]:
        self._errors = []                        # fresh slate for each call
        self._validate(field, value, **context)  # child class fills _errors
        return self._errors                      # caller gets the results

    @abstractmethod # If your child class doesn't implement this, Python will refuse to create it
    def _validate(self, field: str, value, **context)-> None:
        pass

    # This is the method every child validator calls when it finds a problem
    def _add_error(self, error_code: str, field: str, value) -> None:
        self._errors.append(  # self._add_error('AMT001', field='amount', value='0'
            ValidationError.from_code(error_code, field=field, value=value)
        )

    @property
    def errors(self) -> List[ValidationError]:
        return self._errors.copy()  # copy prevents callers from mutating internal state

    @property
    def has_errors(self) -> bool:
        return len(self._errors) > 0  # quick check without exposing the list