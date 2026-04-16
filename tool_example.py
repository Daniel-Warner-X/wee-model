"""
Example of using tool/function calling with the Garbage Model API.
"""

import json
import os
import requests

# Configuration
API_URL = "http://localhost:8080"
API_KEY = os.getenv("API_KEY", "your-api-key-here")

# Define tools/functions available to the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a mathematical calculation",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate, e.g. '2 + 2'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


def get_current_weather(location: str, unit: str = "fahrenheit") -> dict:
    """Mock function to get weather - in reality, this would call a weather API."""
    return {
        "location": location,
        "temperature": 72 if unit == "fahrenheit" else 22,
        "unit": unit,
        "condition": "sunny"
    }


def calculate(expression: str) -> dict:
    """Safely evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


def call_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool call."""
    if tool_name == "get_current_weather":
        return get_current_weather(**arguments)
    elif tool_name == "calculate":
        return calculate(**arguments)
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def chat_with_tools(user_message: str):
    """Send a message and handle tool calls."""
    messages = [{"role": "user", "content": user_message}]

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    print(f"\n{'='*60}")
    print(f"User: {user_message}")
    print(f"{'='*60}")

    # Allow multiple rounds of tool calling
    max_iterations = 5
    for iteration in range(max_iterations):
        payload = {
            "messages": messages,
            "temperature": 0.7,
            "tools": tools
        }

        response = requests.post(
            f"{API_URL}/chat",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return

        result = response.json()

        # Check if model wants to call tools
        if result.get("tool_calls"):
            print(f"\n🔧 Model requested {len(result['tool_calls'])} tool call(s):")

            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": result.get("content", ""),
                "tool_calls": result["tool_calls"]
            })

            # Execute each tool call
            for tool_call in result["tool_calls"]:
                function_name = tool_call["function"]["name"]
                function_args = tool_call["function"]["arguments"]

                print(f"  - {function_name}({json.dumps(function_args)})")

                # Execute the tool
                tool_result = call_tool(function_name, function_args)

                print(f"    → {json.dumps(tool_result)}")

                # Add tool response to messages
                messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_result)
                })

            # Continue the loop to get final answer
            continue

        # No tool calls - we have the final answer
        if result.get("content"):
            print(f"\nAssistant: {result['content']}")

        break
    else:
        print("\n⚠️  Max iterations reached")

    print(f"{'='*60}\n")


def main():
    """Run examples."""
    print("\n🗑️  Tool Calling Examples with Garbage Model API\n")

    # Example 1: Weather query
    chat_with_tools("What's the weather like in San Francisco?")

    # Example 2: Math calculation
    chat_with_tools("What is 15 * 23 + 42?")

    # Example 3: Multiple tools
    chat_with_tools(
        "What's the weather in Boston and what is the temperature in Celsius times 2?"
    )


if __name__ == "__main__":
    main()
