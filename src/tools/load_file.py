from typing import Any
import openpyxl
from PIL import Image
from pydub import AudioSegment

from src.utils.tooling import tool

@tool
def load_file(file_path: str) -> Any:
    """
    Loads data from a file based on its extension.
    Args:
        file_path (str): The path to the file to be loaded.
    """
    file_extension = file_path.split('.')[-1].lower()

    try:
        if file_extension == 'mp3':                         # Load an MP3 audio file
            data = AudioSegment.from_mp3(file_path)

        elif file_extension == 'xlsx':                      # Load an Excel file
            workbook = openpyxl.load_workbook(file_path)
            data = {sheet: [[cell.value for cell in row] for row in sheet.iter_rows()] for sheet in workbook}

        elif file_extension == 'png':                       # Load a PNG image
            data = Image.open(file_path)

        elif file_extension == 'py':                        # Load a Python file
            with open(file_path, 'r') as file:
                data = file.read()

        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        return data

    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None
