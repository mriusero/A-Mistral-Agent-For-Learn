import yaml

def load_prompt():
    """
    Load the prompt templates from YAML files.
    """
    file_paths = {
        "system_prompt": "./prompts/system_prompt.yaml",
        "planning": "./prompts/planning.yaml",
        "managed_agent": "./prompts/managed_agent.yaml",
        "final_answer": "./prompts/final_answer.yaml"
    }
    prompt_template = {}
    for key, path in file_paths.items():
        with open(path, 'r') as stream:
            prompt_template[key] = yaml.safe_load(stream)[key]
    return prompt_template