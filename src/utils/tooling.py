from functools import wraps
import json
import inspect
import re

def generate_tools_json(functions):
    """
    Generates a JSON representation of the tools based on the provided functions.
    """
    tools = []
    for func in functions:
        tools.append(func.tool_info)

    with open('tools.json', 'w') as file:
        json.dump(tools, file, indent=4)

    return {
        "tools": tools
    }

def tool(func):
    """
    Decorator to get function information for tool generation.
    Args:
        func: The function to be decorated.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    description = func.__doc__.strip() if func.__doc__ else "No description available."

    sig = inspect.signature(func)
    parameters = {}
    required = []

    for param_name, param in sig.parameters.items():
        param_type = param.annotation
        if param_type == param.empty:
            param_type = "string"
        else:
            param_type = param_type.__name__
            if param_type == 'str':
                param_type = 'string'
            elif param_type == 'int':
                param_type = 'integer'
            elif param_type == 'list':
                param_type = 'array'
            elif param_type == 'float':
                param_type = 'number'
            elif param_type == 'bool':
                param_type = 'boolean'
            elif param_type == 'dict':
                param_type = 'object'

        param_description = f"The {param_name}."

        docstring_lines = description.split('\n')
        for line in docstring_lines:
            match = re.match(rf"\s*{param_name}\s*\(.*\):\s*(.*)", line)
            if match:
                param_description = match.group(1).strip()
                break

        parameters[param_name] = {
            "type": param_type,
            "description": param_description,
        }

        if param.default == param.empty:
            required.append(param_name)

    wrapper.tool_info = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description.split('\n')[0],
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }
    return wrapper
