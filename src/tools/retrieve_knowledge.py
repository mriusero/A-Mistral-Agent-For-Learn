from src.utils.tooling import tool

@tool
def retrieve_knowledge(query: str, n_results: int = 5, distance_threshold : float = 0.5) -> str:
    """
    Retrieves knowledge from a database with a provided query.
    Args:
        query (str): The query to search for in the vector store.
        n_results (int, optional): The number of results to return. Default is 5.
        distance_threshold (float, optional): The minimum distance score for results. Default is 0.5.
    """
    try:
        from src.utils.vector_store import retrieve_from_database
        results = retrieve_from_database(
            query=query,
            n_results=n_results,
            distance_threshold=distance_threshold
        )
        return str(results)

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"