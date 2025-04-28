import gradio as gr
import pandas as pd
import json
import os
import time
import re
from rich.console import Console
from rich.panel import Panel

from src.utils import (
    fetch_questions,
    submit_answers,
    get_file,
)
from src.inference import Agent

def run_and_submit_all(profile: gr.OAuthProfile | None):
    console = Console()
    space_id = os.getenv("SPACE_ID")

    if profile:
        username = f"{profile.username}"
        console.print(f"User logged in: {username}", style="bold green")
    else:
        console.print("User not logged in.", style="bold red")
        return "Please Login to Hugging Face with the button.", None

    agent_code = f"https://huggingface.co/spaces/{space_id}/tree/main"
    console.print(agent_code)

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
            console.rule(f"\n[bold blue]Task ID: {task_id}")
            console.print(Panel(f"[bold]Question[/bold]\n{question_text}{file_context}", expand=False))

            with open('./metadata.jsonl', 'r') as file:
                for line in file:
                    item = json.loads(line)
                    if item.get('task_id') == task_id:
                        final_answer = item.get('Final answer')

            agent = Agent()
            submitted_answer = agent.run(
                input=question_text + file_context,
                task_id=task_id,
                truth=final_answer
            )

            console.print(Panel(f"[bold green]Submitted Answer[/bold green]\n{submitted_answer}", expand=False))
            console.print(Panel(f"The correct final answer is: [bold]{final_answer}[/bold]"))

            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer})
            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})

        except Exception as e:
            console.print(f"Error: {e}", style="bold red")
            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": f"AGENT ERROR: {e}"})

        time.sleep(1) # Rate limit for API calls

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
