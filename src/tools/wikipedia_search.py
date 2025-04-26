import wikipedia

from src.utils.tooling import tool

@tool
def wikipedia_search(query: str, section: str = None, max_depth: int = 1) -> str:
    """
    This tool searches for specific information on Wikipedia based on a given question or topic.
    The tool can navigate through related pages and extract detailed information from various sections.
    Args:
        query (str): The search query or topic to look up on Wikipedia.
        section (str, optional): The specific section of the Wikipedia page to extract information from. Defaults to None.
        max_depth (int, optional): The maximum depth of navigation through related pages. Defaults to 1.
    """
    try:
        return _search_page(query, section, max_depth)
    except Exception as e:
        return f"An error occurred: {str(e)}"

def _search_page(query: str, section: str, max_depth: int, current_depth: int = 0) -> str:
    if current_depth > max_depth:
        return "Maximum navigation depth reached."

    try:
        page = wikipedia.page(query)
        result = ""
        if section:
            if section in [s.title for s in page.sections]:
                result += page.section(section)
            else:
                return f"Section '{section}' not found in the page."
        else:
            result += page.summary

        related_info = _navigate_related_pages(page, section, max_depth, current_depth + 1)
        if related_info:
            result += "\n\nRelated Pages:\n" + related_info

        return result

    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options
        return f"Disambiguation error. Please choose one of the following options: {', '.join(options)}"

    except wikipedia.exceptions.PageError:
        search_results = wikipedia.search(query)
        if search_results:
            return f"Page not found. Did you mean one of these? {', '.join(search_results)}"
        else:
            return "No results found. Please refine your query."

    except wikipedia.exceptions.RedirectError as e:
        return _search_page(e.title, section, max_depth, current_depth + 1)

    except Exception as e:
        return f"An error occurred: {str(e)}"


def _navigate_related_pages(page, section: str, max_depth: int, current_depth: int) -> str:
    if current_depth > max_depth:
        return "Maximum navigation depth reached."

    related_pages = []
    for link in page.links:
        try:
            related_page = wikipedia.page(link)
            if section:
                if section in [s.title for s in related_page.sections]:
                    related_pages.append(related_page.section(section))
            else:
                related_pages.append(related_page.summary)
        except Exception as e:
            continue

    if not related_pages:
        return "No related pages found."

    return "\n\n".join(related_pages)
