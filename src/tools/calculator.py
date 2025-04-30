from src.utils.tooling import tool
import math
from typing import Union

@tool
def calculator(operation: str, a: float, b: Union[float, None] = None) -> float:
    """
    Performs various calculator operations.
    Args:
        operation (str): The operation to perform. Supported operations are 'add', 'subtract', 'multiply', 'divide', 'power', 'sqrt', 'sin', 'cos', 'tan'.
        a (float): The first number or the angle in radians for trigonometric functions.
        b (float, optional): The second number, required for operations 'add', 'subtract', 'multiply', 'divide', and 'power'.
    Returns:
        float: The result of the operation.
    Raises:
        ValueError: If the operation is not supported or if invalid arguments are provided.
    """
    if operation == 'add':
        if b is None:
            raise ValueError("Second number is required for addition.")
        return a + b

    elif operation == 'subtract':
        if b is None:
            raise ValueError("Second number is required for subtraction.")
        return a - b

    elif operation == 'multiply':
        if b is None:
            raise ValueError("Second number is required for multiplication.")
        return a * b

    elif operation == 'divide':
        if b is None:
            raise ValueError("Second number is required for division.")
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    elif operation == 'power':
        if b is None:
            raise ValueError("Exponent is required for power operation.")
        return math.pow(a, b)

    elif operation == 'sqrt':
        if a < 0:
            raise ValueError("Cannot calculate the square root of a negative number.")
        return math.sqrt(a)

    elif operation == 'sin':
        return math.sin(a)

    elif operation == 'cos':
        return math.cos(a)

    elif operation == 'tan':
        return math.tan(a)

    else:
        raise ValueError(f"Unsupported operation: {operation}")
