from src.utils.tooling import tool
import PyPDF2
import re

@tool
def analyze_document(file_path: str, keywords: list) -> str:
    """
    Extracts specific information from a PDF or text document based on given keywords.
    Args:
        file_path (str): The path to the PDF or text document to analyze.
        keywords (list): A list of keywords to search for in the document.
    Returns:
        str: The extracted information as text.
    """
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extracts text from a PDF file.
        Args:
            file_path (str): The path to the PDF file.
        Returns:
            str: The extracted text from the PDF.
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfFileReader(file)
                text = ''
                for page_num in range(reader.numPages):
                    page = reader.getPage(page_num)
                    text += page.extract_text()
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF file: {e}")

    def extract_text_from_txt(file_path: str) -> str:
        """
        Extracts text from a text file.
        Args:
            file_path (str): The path to the text file.
        Returns:
            str: The extracted text from the text file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {e}")

    def extract_information(text: str, keywords: list) -> str:
        """
        Extracts information based on keywords from the text.
        Args:
            text (str): The text to analyze.
            keywords (list): A list of keywords to search for in the text.
        Returns:
            str: The extracted information as text.
        """
        extracted_info = []
        for keyword in keywords:
            pattern = re.compile(r'\b{}\b'.format(re.escape(keyword)), re.IGNORECASE)
            matches = pattern.findall(text)
            if matches:
                extracted_info.append(f"Keyword '{keyword}': {', '.join(matches)}")
        return "\n".join(extracted_info)

    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.txt'):
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or text file.")

    return extract_information(text, keywords)