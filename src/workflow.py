import gradio as gr
import pandas as pd
import os
import time
import re

from src.utils import (
    fetch_questions,
    submit_answers,
    get_file,
)
from src.inference import Agent

def run_and_submit_all(profile: gr.OAuthProfile | None):

    agent = Agent()
    space_id = os.getenv("SPACE_ID")

    if profile:
        username = f"{profile.username}"
        print(f"User logged in: {username}")
    else:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    agent_code = f"https://huggingface.co/spaces/{space_id}/tree/main"
    print(agent_code)

    questions_data = fetch_questions()

    if not questions_data:
        return "Failed to fetch questions.", None

    results_log = []
    answers_payload = []

    for item in questions_data:

        task_id = item.get("task_id")
        question_text = item.get("question")
        file_name = item.get("file_name")

        if not task_id or question_text is None:
            continue

        if file_name != "":
            file_path = get_file(task_id)
            file_context = f" You can access to the file here: '{file_path}'."
        else:
            file_context = ""

        try:
            print(f"\n ============= Task ID =============\n {task_id}")
            print(f"\n-- Question --\n",  question_text + file_context)

            response = agent.run(input=question_text + file_context)
            match = re.search(r'FINAL ANSWER:\s*(.*)', response, re.DOTALL)

            if match:
                submitted_answer = match.group(1).strip()
            else:
                submitted_answer = 'No FINAL ANSWER found.'

            print(f"\n-- Response --\, {response}")
            print(f"\n-- Submitted Answer --\n", submitted_answer)

            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer})
            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})

        except Exception as e:
            print(f"Error: {e}")
            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": f"AGENT ERROR: {e}"})

        time.sleep(15) # Rate limit for API calls

    if not answers_payload:
        return "Agent did not produce any answers to submit.", pd.DataFrame(results_log)

    submission_data = {"username": username.strip(), "agent_code": agent_code, "answers": answers_payload}
    result_data = submit_answers(submission_data)

    if result_data:
        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        results_df = pd.DataFrame(results_log)
        return final_status, results_df
    else:
        return "Submission Failed.", pd.DataFrame(results_log)