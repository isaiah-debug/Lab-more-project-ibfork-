"""
The calculate tool evaluates simple arithmetic expressions using the Groq tutorial shape.
"""

import json


TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    },
}


def run_calculate(expression):
    """
    Evaluate a simple arithmetic expression and return a JSON result string.

    >>> run_calculate("2 + 2")
    '{"result": 4}'
    >>> run_calculate("10 - 3")
    '{"result": 7}'
    >>> run_calculate("2 * (3 + 4)")
    '{"result": 14}'
    >>> run_calculate("5 / 2")
    '{"result": 2.5}'
    >>> run_calculate("hello")
    '{"error": "name \\'hello\\' is not defined"}'
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return json.dumps({"result": result})
    except Exception as error:
        return json.dumps({"error": str(error)})
