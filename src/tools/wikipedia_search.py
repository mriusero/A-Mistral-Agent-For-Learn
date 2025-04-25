from smolagents import Tool
import wikipedia

class WikipediaSearchTool(Tool):
    name = "wikipedia_search"
    description = """
    This tool searches for specific information on Wikipedia based on a given question or topic.
    It returns the relevant information as text."""
    inputs = {
        "query": {
            "type": "string",
            "description": "The question or topic to search for on Wikipedia.",
        },
        "language": {
            "type": "string",
            "description": "The language in which to search (e.g., 'en' for English, 'fr' for French).",
            "default": "en",
            "nullable": True
        },
        "section": {
            "type": "string",
            "description": "The specific section to extract from the Wikipedia page.",
            "default": None,
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, query: str, language: str = 'en', section: str = None):
        wikipedia.set_lang(language)
        try:
            page = wikipedia.page(query)                # Search for the page related to the query
            if section:
                if section in page.sections:            # Extract a specific section if requested
                    return page.section(section)
                else:
                    return f"Section '{section}' not found in the page."
            return page.summary

        except wikipedia.exceptions.DisambiguationError as e:       # Handle disambiguation errors by listing options
            options = e.options
            return f"Disambiguation error. Please choose one of the following options: {', '.join(options)}"

        except wikipedia.exceptions.PageError:              # If the page is not found, perform a search and list the best matches
            search_results = wikipedia.search(query)
            if search_results:
                return f"Page not found. Did you mean one of these? {', '.join(search_results)}"
            else:
                return "No results found. Please refine your query."

        except Exception as e:                              # Handle any other exceptions
            return f"An error occurred: {str(e)}"
