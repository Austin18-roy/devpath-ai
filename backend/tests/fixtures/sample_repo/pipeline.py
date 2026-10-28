"""Pipeline workflow orchestrator."""
from calculator import Calculator


def run_pipeline(price: float, tax_rate: float) -> float:
    """Entry point for the data pipeline, invoking Calculator."""
    calc = Calculator()
    return calc.process_order(price, tax_rate)

