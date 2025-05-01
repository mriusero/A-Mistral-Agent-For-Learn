import os
from dotenv import load_dotenv
from mistralai import Mistral
import numpy as np
import time
import chromadb
import json

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
COLLECTION_NAME = "webpages_collection"
PERSIST_DIRECTORY = "./chroma_db"

def get_text_embeddings(input_texts):
    """
    Get the text embeddings for the given inputs using Mistral API.
    """
    client = Mistral(api_key=MISTRAL_API_KEY)
    while True:
        try:
            embeddings_batch_response = client.embeddings.create(
                model="mistral-embed",
                inputs=input_texts
            )
            return [data.embedding for data in embeddings_batch_response.data]
        except Exception as e:
            if "rate limit exceeded" in str(e).lower():
                print("Rate limit exceeded. Retrying after 1 second...")
                time.sleep(1)
            else:
                raise

def vectorize(markdown_content, chunk_size=2048):
    """
    Vectorizes the given markdown content into chunks of specified size.
    """
    chunks = [markdown_content[i:i + chunk_size] for i in range(0, len(markdown_content), chunk_size)]
    text_embeddings = get_text_embeddings(chunks)
    return np.array(text_embeddings), chunks

def load_in_vector_db(text_embeddings, chunks, metadatas=None, collection_name=COLLECTION_NAME):
    """
    Load the text embeddings into a ChromaDB collection for efficient similarity search.
    """
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

    # Check if the collection exists, if not, create it
    if collection_name not in [col.name for col in client.list_collections()]:
        collection = client.create_collection(collection_name)
    else:
        collection = client.get_collection(collection_name)

    for embedding, chunk in zip(text_embeddings, chunks):
        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[metadatas],
            ids=[str(hash(chunk))]
        )


def see_database(collection_name=COLLECTION_NAME):
    """
    Load the ChromaDB collection and text chunks.
    """
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

    if collection_name not in [col.name for col in client.list_collections()]:
        print("Collection not found. Please ensure it is created.")
        return

    collection = client.get_collection(collection_name)

    items = collection.get()

    print(f"Type of items: {type(items)}")
    print(f"Items: {items}")

    for item in items:
        print(f"Type of item: {type(item)}")
        print(f"Item: {item}")

        if isinstance(item, dict):
            print(f"ID: {item.get('ids')}")
            print(f"Document: {item.get('document')}")
            print(f"Metadata: {item.get('metadata')}")
        else:
            print("Item is not a dictionary")

        print("---")

def retrieve_from_database(query, collection_name=COLLECTION_NAME, n_results=5, distance_threshold=None):
    """
    Retrieve the most similar documents from the vector store based on the query.
    """
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = client.get_collection(collection_name)
    query_embeddings = get_text_embeddings([query])
    raw_results = collection.query(
        query_embeddings=query_embeddings,
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    if distance_threshold is not None:
        filtered_results = {
            "ids": [],
            "distances": [],
            "metadatas": [],
            "documents": []
        }
        for i, distance in enumerate(raw_results['distances'][0]):
            if distance >= distance_threshold:
                filtered_results['ids'].append(raw_results['ids'][0][i])
                filtered_results['distances'].append(distance)
                filtered_results['metadatas'].append(raw_results['metadatas'][0][i])
                filtered_results['documents'].append(raw_results['documents'][0][i])
        results = filtered_results

        if len(results['documents']) == 0:
            return "No relevant data found in knowledge database, have you visited webpages?"
        else:
            return json.dumps(results, indent=4)
    else:
        return json.dumps(raw_results, indent=4)