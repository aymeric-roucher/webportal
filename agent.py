import json

import requests
from dotenv import load_dotenv
from smolagents import (
    CodeAgent,
    OpenAIModel,
    tool,
)

load_dotenv()

model = OpenAIModel(
    model_id="gpt-4.1"
)  # "gpt-4o" for performance, "gpt-3.5-turbo" for testing


with open("digested_websites/github/^repo_name/issues.md", "r") as f:
    interaction_description = f.read()

instructions = f"""
# Web Task Automation Agent

You are an advanced web automation agent specialized in performing complex tasks through API interactions. 

You are given this description of inbteractive elements for the domain 'github' that you're on:
Since you don't have access to the interactive elements, you can use the GET or POST requests described to mimick the interactions.

To access a specific github issue, head to https://github.com/numpy/numpy/issues/$issue_number with GET request.

{interaction_description}
"""


base_headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
    "github-verified-fetch": "true",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


@tool
def get_request(url: str, params: dict | None = None) -> dict:
    """
    Launch a GET request to the given URL with query parameters.

    Args:
        url (str): The URL to send the GET request to
        params (dict): Query parameters to include in the request
    """
    if params is None:
        params = {}

    try:
        # JSON-encode any dictionary values in params for proper URL encoding
        processed_params = {}
        for key, value in params.items():
            if isinstance(value, dict):
                processed_params[key] = json.dumps(value)
            else:
                processed_params[key] = value

        response = requests.get(
            url, headers=base_headers | {"referer": url}, params=processed_params
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"Error in GET request: {e}"
        return {"error": error_msg}


@tool
def post_request(
    url: str, data: dict | None = None, params: dict | None = None
) -> dict:
    """
    Launch a POST request to the given URL with JSON data and optional query parameters.

    Args:
        url (str): The URL to send the POST request to
        data (dict): JSON data to include in the request body
        params (dict): Query parameters to include in the request
    """
    if data is None:
        data = {}
    if params is None:
        params = {}

    if isinstance(data, dict) and "body" in data:
        data = data["body"]

    if isinstance(data, str):
        data = json.loads(data)

    try:
        post_data = {**data} if data else {}
        post_data.update(params)
        response = requests.post(
            url,
            headers=base_headers | {"content-type": "application/json", "referer": url},
            json=post_data,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"Error in POST request: {e}"
        return {"error": error_msg}


if __name__ == "__main__":
    agent = CodeAgent(
        model=model,
        # tools=[get_manifest_json, post_pull_request_review_decisions],
        tools=[],
        instructions=instructions,
        additional_authorized_imports=["requests", "json"],
        verbosity_level=2,
    )

    task = "Get the appropriate label for Regression on github issues for numpy. Always use the headers attached"

    agent.run(task, additional_tools={"headers_to_use": base_headers})
