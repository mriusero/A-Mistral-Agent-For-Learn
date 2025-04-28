from src.utils.tooling import tool

@tool
def reverse_text(input_text: str) -> str:
    """
    Reverses an input string to make it readable.
    Args:
        input_text (str): The reversed text string to process.
    """
    try:
        corrected_text = input_text[::-1]

        if not corrected_text:
            raise ValueError("The input text is empty! Please provide a valid reversed text string.")

        return corrected_text

    except Exception as e:
        raise Exception(f"An error occurred while processing the text: {e}")