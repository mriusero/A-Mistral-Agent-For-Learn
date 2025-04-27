import os
import re
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

class Agent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        self.client = Mistral(api_key=self.api_key)
        self.model = "codestral-latest"
        self.names_to_functions = {
            "web_search": web_search,
            "visit_webpage": visit_webpage,
            "load_file": load_file,
        }
        self.conversation_log = []

    def get_tools(self):
        """Generate the tools.json file with the tools to be used by the agent."""
        return generate_tools_json(
            [web_search, visit_webpage, load_file]).get('tools')

    def make_initial_request(self, input):
        """Make the initial request to the agent with the given input."""
        with open("./prompt.md", 'r', encoding='utf-8') as file:
            prompt = file.read()

        tools = self.get_tools()
        messages = [
            {"role": "system", "content": prompt},
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
            "tool_choice": 'auto',
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "n": 1,
            "prediction": None,
            "parallel_tool_calls": None
        }
        self.conversation_log.extend(messages)
        return self.client.agents.complete(**payload), messages

    def thought(self, response):
        """Generate a thought based on the current response."""
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                thought_action_observation = choice.message.content
                print(thought_action_observation)
                self.conversation_log.append({"role": "assistant", "content": thought_action_observation})
                return thought_action_observation
        return None

    def act(self, tool_calls):
        """Execute the actions based on the tool calls."""
        results = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            print(f"\nAction: Calling function {function_name} with params {function_params}")

            try:
                function_result = self.names_to_functions[function_name](**function_params)
                results.append((tool_call.id, function_name, function_result))
                print(f"\nTools `{function_name}` returned :\n{function_result}")
                self.conversation_log.append({"role": "tool", "name": function_name, "params": function_params, "result": function_result})
            except Exception as e:
                print(f"Error calling function {function_name}: {e}")
                results.append((tool_call.id, function_name, None))
                self.conversation_log.append({"role": "tool", "name": function_name, "params": function_params, "result": None, "error": str(e)})

        return results

    def observe(self, messages, results):
        """Generate an observation based on the results of the actions."""
        for tool_call_id, function_name, function_result in results:
            messages.append(
                {
                    "role": "assistant",
                    "content": f"{function_name}: {function_result}",
                    "prefix": True,
                    "tool_call_id": tool_call_id
                }
            )
            self.conversation_log.append({"role": "assistant", "content": f"{function_name}: {function_result}", "tool_call_id": tool_call_id})
        return messages

    def save_conversation(self, task_id, truth, final_answer=None):
        """Save the conversation log to a JSON file with a timestamped filename."""
        filename = f"./logs/{task_id}.json"
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(
                self.conversation_log + [{"Correct Answer": truth, "Final Answer": final_answer}],
                file, ensure_ascii=False, indent=4
            )

    def run(self, input, task_id, truth, max_steps=20):
        """Run the agent with the given input and process the response."""
        print("\n... Asking the agent ...\n")
        response, messages = self.make_initial_request(input)
        steps = 0

        while steps < max_steps:
            steps += 1
            thought_result = self.thought(response)

            final_answer_match = re.search(r'Final Answer\n(.*)', thought_result, re.DOTALL)
            if final_answer_match:
                self.save_conversation(task_id, truth, final_answer_match.group(1).strip())
                return final_answer_match.group(1).strip()

            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]

                if choice.message.tool_calls:
                    action_results = self.act(choice.message.tool_calls)

                    time.sleep(1)

                    messages = self.observe(messages, action_results)

                    response = self.client.chat.complete(
                        model=self.model,
                        messages=messages
                    )
                    time.sleep(1)
                else:
                    print("No tool calls in choice message.")
                    break
            else:
                print("No valid response from the agent.")
                return "No valid response from the agent."

        self.save_conversation(task_id, truth)
        return "Max steps reached. No final answer found."
