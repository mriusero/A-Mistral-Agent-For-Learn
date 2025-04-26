from smolagents import Tool
import wikipedia

class WikipediaSearchTool(Tool):
    name = "wikipedia_search"
    description = """
    This tool searches for specific information on Wikipedia based on a given question or topic.
    The tool can navigate through related pages and extract detailed information from various sections."""

    inputs = {
        "query": {
            "type": "string",
            "description": "The main question or topic to search for on Wikipedia.",
        },
    #    "language": {
    #        "type": "string",
    #        "description": "The language in which to search (e.g., 'en' for English, 'fr' for French).",
    #        "default": "en",
    #        "nullable": True
    #    },
        "section": {
            "type": "string",
            "description": "The specific section to extract from the Wikipedia page (ex: discography).",
            "default": None,
            "nullable": True
        },
        "max_depth": {
            "type": "integer",
            "description": "The maximum depth to navigate through related pages.",
            "default": 1,
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, query: str, section: str = None, max_depth: int = 1):
        try:
            return self._search_page(query, section, max_depth)
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def _search_page(self, query: str, section: str, max_depth: int, current_depth: int = 0):
        if current_depth > max_depth:
            return "Maximum navigation depth reached."

        try:
            page = wikipedia.page(query)
            if section:
                if section in [s.title for s in page.sections]:
                    return page.section(section)
                else:
                    return f"Section '{section}' not found in the page."
            return page.summary

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
            return self._search_page(e.title, section, max_depth, current_depth + 1)

        except Exception as e:
            return f"An error occurred: {str(e)}"

    def _navigate_related_pages(self, page, section: str, max_depth: int, current_depth: int):
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
