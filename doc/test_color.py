# TODO: This is a comment for color testing
"""
This is a docstring - multi-line string
Used for documentation and should have its own color
"""

from datetime import datetime
import pandas as pd


class DataProcessor:
    """Main class for processing data - testing class names"""

    def __init__(self, name: str, threshold: int = 100):
        # Instance variables
        self.name = name
        self.threshold = threshold
        self._private_var = 42
        self.data_list = [1, 2, 3, 4, 5]
        self.data_dict = {"key": "value", "number": 123}

    @staticmethod
    def validate_input(value: float) -> bool:
        """Decorator and return type testing"""
        return value > 0 and value != 999

    def process_data(self, input_data: list) -> dict:
        """Method with operators, f-strings, and logic"""
        # Arithmetic operators
        result = (10 + 20) * 3 - 5 / 2

        # Comparison operators
        if result >= 50 and result <= 100:
            status = "valid"
        elif result != 0:
            status = "warning"
        else:
            status = "error"

        # F-string with expressions
        message = f"Processing {self.name}: result={result:.2f}, status='{status}'"

        # Lambda function
        squared = lambda x: x ** 2

        # List comprehension
        processed = [squared(x) for x in input_data if x > self.threshold]

        # Dictionary comprehension
        mapping = {f"item_{i}": val for i, val in enumerate(processed)}

        # Walrus operator (assignment expression)
        if (n := len(processed)) > 0:
            print(f"Processed {n} items")

        # Arrow function style (not really Python but for ->)
        # In type hints: Callable[[int], str]

        return {
            "result": result,
            "message": message,
            "data": mapping,
            "timestamp": datetime.now()
        }


# Function definition
def calculate_metrics(values: list[float], *, debug: bool = False) -> tuple[float, float]:
    """Testing function colors, type hints, keyword-only args"""
    total = sum(values)
    average = total / len(values)

    # Ternary operator
    status = "high" if average > 50 else "low"

    # Raw string
    pattern = r"\d+\.\d+"

    # Bytes
    data_bytes = b"binary data"

    # None, True, False, keywords
    result = None
    is_valid = True
    has_errors = False

    # Try-except
    try:
        risky_calc = 100 / (average - average)
    except ZeroDivisionError as e:
        print(f"Error: {e}")
        raise ValueError("Cannot divide by zero") from e
    finally:
        pass

    return (total, average)


# Main execution
if __name__ == "__main__":
    # Creating instance
    processor = DataProcessor("TestProcessor", threshold=50)

    # Numbers: int, float, hex, binary
    numbers = [42, 3.14159, 0xFF, 0b1010, 1_000_000]

    # Strings: single, double, triple
    single = 'single quotes'
    double = "double quotes"
    triple = '''triple single'''

    # Method call with operators
    result = processor.process_data(numbers)

    # Boolean operators
    condition = (result and True) or (not False)

    # Membership and identity
    is_member = "key" in result
    is_same = result is not None

    # Async/await keywords (even if not really async here)
    # async def fetch_data(): await something

    print(f"Done! Result: {result}")