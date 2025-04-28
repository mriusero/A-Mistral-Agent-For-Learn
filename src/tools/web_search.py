from src.utils.tooling import tool

@tool
def web_search(query: str, max_results: int = 3, timeout: int = 1) -> str:
    """
    Performs a web search based on the query and returns the top search results.
    Args:
        query (str): The search query to perform.
        max_results (int, optional): The maximum number of results to return. Defaults to 10.
        timeout (int, optional): Timeout for the search request in seconds. Defaults to 10.
        region (str, optional): Region code for the search. Defaults to 'wt-wt' (worldwide).
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError as e:
        raise ImportError(
            "You must install package `duckduckgo_search` to run this tool: for instance run `pip install duckduckgo-search`."
        ) from e

    ddgs = DDGS(timeout=timeout)
    results = ddgs.text(query, max_results=max_results)

    if len(results) == 0:
        raise Exception("No results found! Try a less restrictive/shorter query.")

    postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
    return "## Search Results\n\n" + "\n\n".join(postprocessed_results)
