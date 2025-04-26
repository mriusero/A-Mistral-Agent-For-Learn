import re

from src.utils.tooling import tool

@tool
def visit_webpage(url: str) -> str:
    """
    Visits a webpage at the given URL and reads its content as a markdown string.
    Args:
        url (str): The URL of the webpage to visit.
    """
    try:
        import requests
        from markdownify import markdownify
        from requests.exceptions import RequestException
        from smolagents.utils import truncate_content

    except ImportError as e:
        raise ImportError(
            "You must install packages `markdownify` and `requests` to run this tool: for instance run `pip install markdownify requests`."
        ) from e

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()                         # Raise an exception for bad status codes

        markdown_content = markdownify(response.text).strip()                            # Convert the HTML content to Markdown
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)      # Remove multiple line breaks

        return truncate_content(markdown_content, 10000)

    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later or check the URL."

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"