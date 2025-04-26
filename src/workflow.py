import gradio as gr
import pandas as pd
import os
import time
from dotenv import load_dotenv

from smolagents import CodeAgent, MLXModel, DuckDuckGoSearchTool

from src.utils import (
    fetch_questions,
    submit_answers,
    get_file,
    validate_answer,
    load_prompt
)
from src.tools import (
    WikipediaSearchTool,
    VisitWebpageTool,
    FileLoaderTool,
    FinalAnswerTool,
)

load_dotenv()

def run_and_submit_all(profile: gr.OAuthProfile | None):
    space_id = os.getenv("SPACE_ID")
    if profile:
        username = f"{profile.username}"
        print(f"User logged in: {username}")
    else:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    # Load the model
    mlx_model = MLXModel(
        model_id="./llm/Qwen2.5-Coder-14B-Instruct-bf16",
        tool_name_key='name',                                       # ID for fetch tools
        tool_arguments_key='inputs',                                # ID for fetch tool arguments
        trust_remote_code=False,
        max_tokens=128000
    )

    # Load tools
    wikipedia_search_tool = WikipediaSearchTool()
    web_search = DuckDuckGoSearchTool()
    visit_webpage = VisitWebpageTool()
    file_loader = FileLoaderTool()
    final_answer = FinalAnswerTool()

    # Load prompt template
    prompt_template = load_prompt()

    # Initialize the agent
    agent = CodeAgent(
        model=mlx_model,
        tools=[
            wikipedia_search_tool,
            web_search,
            visit_webpage,
            file_loader,
            final_answer,
        ],
        add_base_tools=True,
        max_steps=30,
        verbosity_level=5,
        grammar=None,
        planning_interval=None,
        name=None,
        description=None,
        prompt_templates=prompt_template,
        additional_authorized_imports = ['requests', 'bs4', 'wiki'],
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
        file_name = item.get("file_name")
        if not task_id or question_text is None:
            continue

        if file_name != "":
            file_path = get_file(task_id)
            add_context = f" You can access to the file here: '{file_path}'."
        else:
            add_context = ""

        try:
            submitted_answer = agent.run(question_text + add_context)
            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer})
            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})

        except Exception as e:
            results_log.append({"Task ID": task_id, "Question": question_text, "Submitted Answer": f"AGENT ERROR: {e}"})

        time.sleep(120) # Tempo to avoid throttling

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