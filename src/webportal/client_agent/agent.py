import json
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from markdownify import markdownify
from smolagents import (
    CodeAgent,
    OpenAIModel,
    tool,
)
from webportal.common import WEBPORTAL_REPO_PATH
load_dotenv()

model = OpenAIModel(
    model_id="gpt-4o-mini"  # for 200k token per minute
)  # "gpt-4o" for performance, "gpt-3.5-turbo" for testing


with open(WEBPORTAL_REPO_PATH / "digested_websites/github_generated.md", "r") as f:
    interaction_description = f.read()

instructions = f"""
# Web Task Automation Agent

You are an advanced web automation agent specialized in performing complex tasks through API interactions. 

Below is a description of the API calls that you can make to the desired domain.
You cannot use them directly, you need to use the tools provided to you.

Here is the description of the API calls:
{interaction_description}

"""


base_headers = {
    "sec-fetch-site": "same-origin",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
    "github-verified-fetch": "true",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


@tool
def get_request(url: str, params: dict | None = None) -> dict:
    """
    Launch a GET request to the given URL with query parameters.

    Args:
        url (str): The URL to send the GET request to
        params (dict): Query parameters to include in the request. Encode them as objects.
    """
    if params is None:
        params = {}
        
    time.sleep(2)

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
        # Try to parse as JSON, but if not possible, return the raw text (e.g. HTML)
        try:
            result = response.json()
            # Check for GraphQL-style errors in successful responses
            if isinstance(result, dict) and "errors" in result:
                return {"error": f"API returned errors: {result['errors']}"}
            return result
        except json.JSONDecodeError:
            # Not JSON, extract data from HTML and script tags
            html_content = response.text

            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract JSON data from script tags
            script_data = ""

            # Look for script tags with JSON data
            for script in soup.find_all("script"):
                if "data-target=" in str(script):
                    script_data += "\n" + str(script)
            result = {"content": markdownify(html_content)}
            print("SCRIPTDATA\n", script_data)
            if script_data:
                result["extracted_data"] = script_data

            return result
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
    time.sleep(2)
    
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
        result = response.json()

        # Check for GraphQL-style errors in successful responses
        if isinstance(result, dict) and "errors" in result:
            return {"error": f"API returned errors: {result['errors']}"}

        return result
    except requests.exceptions.RequestException as e:
        error_msg = f"Error in POST request: {e}"
        return {"error": error_msg}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON response: {e}"}


if __name__ == "__main__":
    agent = CodeAgent(
        model=model,
        tools=[get_request, post_request],
        instructions=instructions,
        additional_authorized_imports=["urllib.*"],
        verbosity_level=2,
    )

    task = "According to github, when was Regression added to the oldest closed numpy.polynomial issue that has the Regression label in MM/DD/YY?"

    agent.run(task)
