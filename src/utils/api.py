import os
import requests

DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"

def fetch_questions(api_url=DEFAULT_API_URL):
    """
    Fetches questions from the API.
    Args:
        api_url (str): The base URL of the API.
    Returns:
        list: A list of questions if successful, None otherwise.
    """
    questions_url = f"{api_url}/questions"
    try:
        response = requests.get(questions_url, timeout=15)
        response.raise_for_status()
        questions_data = response.json()

        if not questions_data:
            print("Fetched questions list is empty.")
            return None

        print(f"Fetched {len(questions_data)} questions.")
        return questions_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching questions: {e}")
        return None

    except Exception as e:
        print(f"An unexpected error occurred fetching questions: {e}")
        return None


def submit_answers(submission_data, api_url=DEFAULT_API_URL):
    """
    Submits answers to the API.
    Args:
        submission_data (dict): The data to be submitted.
        api_url (str): The base URL of the API.
    Returns:
        dict: The response from the API if successful, None otherwise.
    """
    submit_url = f"{api_url}/submit"
    print(f"Submitting answers to: {submit_url}")
    try:
        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
        return result_data

    except requests.exceptions.RequestException as e:
        print(f"Submission Failed: {e}")
        return None


def get_file(task_id, api_url=DEFAULT_API_URL):
    """
    Fetches a file associated with a task ID from the API.
    Args:
        task_id (str): The ID of the task.
        api_url (str): The base URL of the API.
    Returns:
        str: The path to the saved file if successful, None otherwise.
    """
    file_url = f"{api_url}/files/{task_id}"
    try:
        response = requests.get(file_url, timeout=15)
        response.raise_for_status()

        content_disposition = response.headers.get('content-disposition')
        file_name = content_disposition.split('filename="')[1].strip('"')

        directory = "./attachments/"
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, file_name)

        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path

    except Exception as e:
        print(f"An unexpected error occurred fetching file: {e}")
        return None