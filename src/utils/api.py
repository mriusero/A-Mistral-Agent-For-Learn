import requests

DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"

def fetch_questions(api_url=DEFAULT_API_URL):
    questions_url = f"{api_url}/questions"
    print(f"Fetching questions from: {questions_url}")
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