from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from app.utils import tools
import httpx
import json
import os

load_dotenv()

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
AIPROXY_BASE_URL = "https://aiproxy.sanand.workers.dev/openai/v1"


def parse_function_args(function_args):
    if function_args is not None:
        if isinstance(function_args, str):
            function_args = json.loads(function_args)

        elif not isinstance(function_args, dict):
            function_args = {"args": function_args}
    else:
        function_args = {}

    return function_args


async def get_openai_response(question: str, file_path: Optional[str] = None) -> str:
    """
    Get response from OpenAI via AI Proxy
    """

    # Define tools for OpenAI to call
    with open('openai_functions.json', 'r') as file:
        openai_functions = json.load(file)
    
    # Create the messages to send to the API
    messages = [
        {
            "role": "system",
            "content": "You are an assistant designed to solve data science assignment problems. You should use the provided functions when appropriate to solve the problem.",
        },
        {"role": "user", "content": question},
    ]

    # Add information about the file if provided
    if file_path:
        messages.append(
            {
                "role": "user",
                "content": f"I've uploaded a file that you can process. The file is stored at: {file_path}",
            }
        )

    # Prepare the request payload
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "tools": openai_functions,
        "tool_choice": "auto",
    }

    # Make the request to the AI Proxy
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AIPROXY_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60.0,
        )

        if response.status_code != 200:
            raise Exception(f"Error from OpenAI API: {response.text}")

        result = response.json()
        answer = None


        # Process the response
        message = result["choices"][0]["message"]
        if "tool_calls" in message:
            for tool_call in message["tool_calls"]:
                function_name = tool_call["function"].get("name")
                function_args = tool_call["function"].get("arguments")

                # Ensure the function name is valid and callable
                if hasattr(tools, function_name) and callable(getattr(tools, function_name)):
                    function_chosen = getattr(tools, function_name)
                    function_args = parse_function_args(function_args)

                    if isinstance(function_args, dict):
                        answer = await function_chosen(**function_args)
        
        # If no function call was executed, return the content
        if answer is None:
            answer = message.get("content", "No answer could be generated.")

        return answer
