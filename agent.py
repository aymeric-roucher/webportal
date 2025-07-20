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

{interaction_description}
"""


@tool
def launch_request(
    url: str, method: str, params: dict, body: dict | None = None
) -> dict:
    """
    Launch a request to the given URL with the given method, parameters and body.

    Args:
        url (str): The URL of the webpage to visit
        method (str): The HTTP method to use
        params (dict): The parameters to use
        body (dict): The body to use
    """
    if body is None:
        body = {}

    base_headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
        "content-type": "application/json",
        "github-verified-fetch": "true",
        "referer": url,
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    if isinstance(body, dict) and "body" in body:
        body = body["body"]

    try:
        if method == "GET":
            response = requests.get(url, headers=base_headers, params=params, json=body)
        elif method == "POST":
            response = requests.post(
                url, headers=base_headers, params=params, json=body
            )
        else:
            raise ValueError(f"Invalid method: {method}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching branch and tag count: {e}")
        return None


if __name__ == "__main__":
    agent = CodeAgent(
        model=model,
        # tools=[get_manifest_json, post_pull_request_review_decisions],
        tools=[launch_request],
        instructions=instructions,
    )

    task = "According to github, when was Regression added to the oldest closed numpy.polynomial issue that has the Regression label in MM/DD/YY?"

    agent.run(task)
