from src.utils.tooling import tool

def format_the(query, results):

    if results ==  "No relevant data found in the knowledge database. Have you checked any webpages? If so, please try to find more relevant data.":
        return results
    else:
        formatted_text = f"# Knowledge for '{query}' \n\n"
        formatted_text += f"Fetched {len(results['documents'])} relevant documents.\n\n"
        try:
            for i in range(len(results['documents'])):
                formatted_text += f"## Document {i + 1} ---\n"
                formatted_text += f"- Title: {results['metadatas'][i]['title']}\n"
                formatted_text += f"- URL: {results['metadatas'][i]['url']}\n"
                formatted_text += f"- Content: '''\n{results['documents'][i]}\n'''\n"
                formatted_text += f"---\n\n"
        except Exception as e:
            return f"Error: Index out of range. Please check the results structure. {str(e)}"
        return formatted_text

@tool
def retrieve_knowledge(query: str, n_results: int = 2) -> str:
    """
    Retrieves knowledge from a database with a provided query.
    Args:
        query (str): The query to search for in the vector store.
        n_results (int, optional): The number of results to return. Default is 1.
    """
    try:
        from src.utils.vector_store import retrieve_from_database
        distance_threshold = 0.2
        results = retrieve_from_database(
            query=query,
            n_results=n_results,
            distance_threshold=distance_threshold
        )
        #print(results)
        return format_the(query, results)

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

