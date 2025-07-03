import os
from dotenv import load_dotenv
from mistralai import Mistral
import numpy as np
import time
import chromadb
from chromadb.config import Settings
import json
import hashlib

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
COLLECTION_NAME = "webpages_collection"
PERSIST_DIRECTORY = "./chroma_db"

def vectorize(input_texts, batch_size=5):
    """
    Get the text embeddings for the given inputs using Mistral API.
    """
    try:
        client = Mistral(api_key=MISTRAL_API_KEY)
    except Exception as e:
        print(f"Error initializing Mistral client: {e}")
        return []

    embeddings = []

    for i in range(0, len(input_texts), batch_size):
        batch = input_texts[i:i + batch_size]
        while True:
            try:
                embeddings_batch_response = client.embeddings.create(
                    model="mistral-embed",
                    inputs=batch
                )
                time.sleep(1)
                embeddings.extend([data.embedding for data in embeddings_batch_response.data])
                break
            except Exception as e:
                if "rate limit exceeded" in str(e).lower():
                    print("Rate limit exceeded. Retrying after 10 seconds...")
                    time.sleep(10)
                else:
                    print(f"Error in embedding batch: {e}")
                    raise

    return embeddings


def chunk_content(markdown_content, chunk_size=2048):
    """
    Vectorizes the given markdown content into chunks of specified size without cutting sentences.
    """
    def find_sentence_end(text, start):
        """Find the nearest sentence end from the start index."""
        punctuations = {'.', '!', '?'}
        end = start
        while end < len(text) and text[end] not in punctuations:
            end += 1
        while end < len(text) and text[end] in punctuations:
            end += 1
        while end > start and text[end - 1] not in punctuations:
            end -= 1
        return end

    chunks = []
    start = 0

    while start < len(markdown_content):
        end = min(start + chunk_size, len(markdown_content))
        end = find_sentence_end(markdown_content, end)
        chunks.append(markdown_content[start:end].strip())
        start = end

    return chunks


def generate_chunk_id(chunk):
    """Generate a unique ID for a chunk using SHA-256 hash."""
    return hashlib.sha256(chunk.encode('utf-8')).hexdigest()


def load_in_vector_db(markdown_content, metadatas=None, collection_name=COLLECTION_NAME):
    """
    Load the text embeddings into a ChromaDB collection for efficient similarity search.
    """
    try:
        client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    except Exception as e:
        print(f"Error initializing ChromaDB client: {e}")
        return

    try:
        if collection_name not in [col.name for col in client.list_collections()]:
            collection = client.create_collection(collection_name)
        else:
            collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"Error accessing collection: {e}")
        return

    try:
        existing_items = collection.get()
    except Exception as e:
        print(f"Error retrieving existing items: {e}")
        return

    existing_ids = set()

    if 'ids' in existing_items:
        existing_ids.update(existing_items['ids'])

    chunks = chunk_content(markdown_content)
    text_to_vectorize = []

    for chunk in chunks:
        chunk_id = generate_chunk_id(chunk)
        if chunk_id not in existing_ids:
            text_to_vectorize.append(chunk)

    print(f"New chunks to vectorize: {len(text_to_vectorize)}")

    if text_to_vectorize:
        embeddings = vectorize(text_to_vectorize)
        for embedding, chunk in zip(embeddings, text_to_vectorize):
            chunk_id = generate_chunk_id(chunk)
            if chunk_id not in existing_ids:
                try:
                    collection.add(
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[metadatas],
                        ids=[chunk_id]
                    )
                    existing_ids.add(chunk_id)
                except Exception as e:
                    print(f"Error adding embedding to collection: {e}")


def retrieve_from_database(query, collection_name=COLLECTION_NAME, n_results=5, distance_threshold=None):
    """
    Retrieve the most similar documents from the vector store based on the query.
    """
    try:
        client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
        collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"Error accessing collection: {e}")
        return

    try:
        query_embeddings = vectorize([query])
    except Exception as e:
        print(f"Error vectorizing query: {e}")
        return

    try:
        raw_results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        print(f"Error querying collection: {e}")
        return

    if distance_threshold is not None:
        filtered_results = {
            "ids": [],
            "distances": [],
            "metadatas": [],
            "documents": []
        }
        for i, distance in enumerate(raw_results['distances'][0]):
            if distance <= distance_threshold:
                filtered_results['ids'].append(raw_results['ids'][0][i])
                filtered_results['distances'].append(distance)
                filtered_results['metadatas'].append(raw_results['metadatas'][0][i])
                filtered_results['documents'].append(raw_results['documents'][0][i])
        results = filtered_results

        if len(results['documents']) == 0:
            return "No relevant data found in the knowledge database. Have you checked any webpages? If so, please try to find more relevant data."
        else:
            return results
    else:
        return raw_results


def search_documents(collection_name=COLLECTION_NAME, query=None, query_embedding=None, metadata_filter=None, n_results=10):
    """
    Search for documents in a ChromaDB collection.

    :param collection_name: The name of the collection to search within.
    :param query: The text query to search for (optional).
    :param query_embedding: The embedding query to search for (optional).
    :param metadata_filter: A filter to apply to the metadata (optional).
    :param n_results: The number of results to return (default is 10).
    :return: The search results.
    """
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = client.get_collection(collection_name)

    if query:
        query_embedding = vectorize([query])[0]

    if query_embedding:
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results, where=metadata_filter)
    else:
        results = collection.get(where=metadata_filter, limit=n_results)

    return results


def delete_documents(collection_name=COLLECTION_NAME, ids=None):
    """
    Delete documents from a ChromaDB collection based on their IDs.

    :param collection_name: The name of the collection.
    :param ids: A list of IDs of the documents to delete.
    """
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = client.get_collection(collection_name)

    collection.delete(ids=ids)
    print(f"Documents with IDs {ids} have been deleted from the collection {collection_name}.")

def delete_collection(collection_name=COLLECTION_NAME):
    """
    Delete a ChromaDB collection.

    :param collection_name: The name of the collection to delete.
    """
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    client.delete_collection(collection_name)
    print(f"Collection {collection_name} has been deleted.")