import os
import json
import time
from dotenv import load_dotenv
from mistralai import Mistral

from src.utils.tooling import generate_tools_json
from src.tools import (
    web_search,
    visit_webpage,
    load_file,
)

load_dotenv()

PROMPT_SYSTEM="""

# Instructions
You are a general AI assistant.
I will ask you a question.
Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].

## Tools
- web_search: This tool allows you to perform a web search.
- visit_webpage: This tool allows you to visit a webpage and extract information from it.
- load_file: This tool allows you to load a file and extract information from it.

## Tips
- Check if answers are in the tools' output.
- If you are not sure about the answer, you can use another tool to find more information.
- The web_search tool is only here to get urls, you can use the visit_webpage tool to get the content of the page.

## Rules
1. YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
2. If you are asked for a number, don’t use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
3. If you are asked for a string, don’t use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
4. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
"""

class Agent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        self.client = Mistral(api_key=self.api_key)
        self.model = "codestral-latest"

    def get_tools(self):
        """
        Generates the tools.json file with the tools to be used by the agent.
        """
        return generate_tools_json(
            [
                web_search,
                visit_webpage,
                load_file,
            ]
        ).get('tools')

    def make_initial_request(self, input):
        """
        Make the initial request to the agent with the given input.
        """
        tools = self.get_tools()
        messages = [
            {"role": "system", "content": PROMPT_SYSTEM},
            {"role": "user", "content": input},
        ]
        payload = {
            "agent_id": self.agent_id,
            "messages": messages,
            "max_tokens": None,
            "stream": False,
            "stop": None,
            "random_seed": None,
            "response_format": None,
            "tools": tools,
            "tool_choice": 'any',
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "n": 1,
            "prediction": None,
            "parallel_tool_calls": None
        }
        return self.client.agents.complete(**payload), messages

    def process_response(self, response, messages, max_steps):
        """
        Process the response from the agent and iterate until a final answer is found.
        """
        steps = 0
        names_to_functions = {
            "web_search": web_search,
            "visit_webpage": visit_webpage,
            "load_file": load_file,
        }

        while steps < max_steps:
            steps += 1
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]

                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    print(choice.message.content)

                messages.append(response.choices[0].message)

                if response.choices[0].message.tool_calls:
                    for tool_call in response.choices[0].message.tool_calls:
                        function_name = tool_call.function.name
                        function_params = json.loads(tool_call.function.arguments)
                        print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)

                        try:
                            function_result = names_to_functions[function_name](**function_params)
                            print("\nfunction_result: ", function_result)

                            messages.append(
                                {
                                    "role": "tool",
                                    "name": function_name,
                                    "content": function_result,
                                    "tool_call_id": tool_call.id
                                }
                            )

                            time.sleep(1)

                        except Exception as e:
                            print(f"Error calling function {function_name}: {e}")

                    response = self.client.chat.complete(
                        model=self.model,
                        messages=messages
                    )
                    if "FINAL ANSWER:" in response.choices[0].message.content:
                        return response.choices[0].message.content
                else:
                    return "No tool calls were made."
            else:
                return "No valid response from the agent."

        return "Max steps reached. No final answer found."

    def run(self, input, max_steps=5):
        """
        Run the agent with the given input and process the response.
        """
        response, messages = self.make_initial_request(input)
        return self.process_response(response, messages, max_steps)
