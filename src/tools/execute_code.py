from src.utils.tooling import tool
import subprocess
import tempfile

@tool
def execute_code(file_path: str) -> str:
    """
    Executes Python code from a file and returns the final result.
    Args:
        file_path (str): The path to the file containing the Python code to execute.
    Returns:
        str: The result of the code execution.
    """
    try:
        with open(file_path, 'r') as file:
            code = file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file_path = temp_file.name

        result = subprocess.run(['python', temp_file_path], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Error executing code: {result.stderr}")

        return result.stdout

    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")