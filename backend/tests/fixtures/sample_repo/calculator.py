"""Calculator class utilizing math utilities."""
from math_utils import add, multiply


class BaseEngine:
    """Base computational engine."""
    def version(self) -> str:
        return "1.0.0"


class Calculator(BaseEngine):
    """High-level calculation class."""

    def compute_sum(self, x: float, y: float) -> float:
        """Compute sum using imported math_utils.add."""
        return add(x, y)

    def apply_tax(self, amount: float, rate: float) -> float:
        """Apply tax multiplier using imported math_utils.multiply."""
        return multiply(amount, rate)

    def process_order(self, price: float, tax_rate: float) -> float:
        """Process order by computing tax and sum."""
        tax = self.apply_tax(price, tax_rate)
        return self.compute_sum(price, tax)

