import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

PROMPT_SYSTEM="""
You are a general AI assistant. 
I will ask you a question.
Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].
YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
If you are asked for a number, don’t use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
If you are asked for a string, don’t use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
"""

class Agent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        self.client = Mistral(api_key=self.api_key)

    def run(self, input):
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
            "tools": None,
            "tool_choice": 'auto',
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "n": 1,
            "prediction": None,
            "parallel_tool_calls": True
        }
        response = self.client.agents.complete(**payload)

        if isinstance(response, dict) and 'error' in response:
            raise Exception(response['error'])

        #print("Response:", response)

        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]

            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return choice.message.content

        return 'No response content found.'