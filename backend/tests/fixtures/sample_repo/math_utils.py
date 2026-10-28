"""Low-level arithmetic utility functions."""

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def square(x: float) -> float:
    """Calculate the square of a number using multiply."""
    return multiply(x, x)

