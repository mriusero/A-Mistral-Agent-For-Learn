from src.utils.tooling import tool
import pandas as pd

@tool
def analyze_excel(file_path: str, sheet_name: str = None, specific_columns: list = None) -> str:
    """
    Analyzes data from an Excel file to extract specific information.
    Args:
        file_path (str): The path to the Excel file to analyze.
        sheet_name (str, optional): The name of the sheet to read. If None, the first sheet is used.
        specific_columns (list, optional): A list of column names to extract. If None, all columns are extracted.
    Returns:
        str: Extracted information in text or structured data format.
    """
    try:
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)

        if specific_columns:
            df = df[specific_columns]

        return f"Excel file contains:\n\n{df.to_string(index=False)}"

    except FileNotFoundError:
        return "File not found. Please check the file path."
    except pd.errors.EmptyDataError:
        return "The Excel file is empty."
    except pd.errors.ParserError:
        return "Error parsing the Excel file."
    except Exception as e:
        return f"An error occurred: {str(e)}"
