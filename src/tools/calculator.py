from typing import List
from src.utils.tooling import tool

@tool
def calculate_sum(numbers: list[float]) -> float:
    """
    Calculates the sum of a list of numbers.
    WARNING: You have to be sure that the input is coherent to answer correctly to a given question.
    Args:
        numbers (List[float]): A list of numbers to be summed from the question.
    Returns:
        float: The sum of the numbers.
    """
    try:
        total = sum(numbers)
        return f"The sum of the list of number is: {total:.2f}"
    except Exception as e:
        print(f"Error calculating sum: {e}")
        return None