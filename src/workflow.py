import gradio as gr
import pandas as pd
import os
import yaml

from smolagents import CodeAgent, MLXModel, DuckDuckGoSearchTool, load_tool, tool

from src.api import fetch_questions, submit_answers
from src.tools import WikipediaSearchTool, VisitWebpageTool, FinalAnswerTool
from src.final_check import validate_answer


def run_and_submit_all(profile: gr.OAuthProfile | None):
    space_id = os.getenv("SPACE_ID")
    if profile:
        username = f"{profile.username}"
        print(f"User logged in: {username}")
    else:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    with open("./prompt.yaml", 'r') as stream:
        prompt_template = yaml.safe_load(stream)

    # Load the model
    # mlx_model = MLXModel("./Qwen2.5-Coder-32B-Instruct-4bit") too large for local inference
    #mlx_model = MLXModel("./Qwen2.5-Coder-14B-Instruct-bf16")
    mlx_model = MLXModel("./DeepSeek-Coder-V2-Lite-Instruct-8bit")

    # Load tools
    wikipedia_search_tool = WikipediaSearchTool()
    web_search = DuckDuckGoSearchTool()
    visit_webpage = VisitWebpageTool()
    final_answer = FinalAnswerTool()



    agent = CodeAgent(
        model=mlx_model,
        tools=[
            web_search,
            wikipedia_search_tool,
            visit_webpage,
            final_answer,
        ],
        add_base_tools=True,
        max_steps=6,
        verbosity_level=2,
        grammar=None,
        planning_interval=None,
        name=None,
        description=None,
        prompt_templates=prompt_template,
        additional_authorized_imports = ['requests'],
        final_answer_checks=[validate_answer],
    )
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
        if not task_id or question_text is None:
            continue
        try:
            submitted_answer = agent.run(question_text)
            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer})
            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})
        except Exception as e:
            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": f"AGENT ERROR: {e}"})

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