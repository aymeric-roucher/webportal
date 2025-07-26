import json
import time

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from smolagents import tool

from webportal.get_static_page.crawl4ai_tools import get_markdown_using_crawl4ai

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


def _process_params(params: dict | None) -> dict:
    """Process request parameters by JSON-encoding dictionary values."""
    if params is None:
        return {}

    processed_params = {}
    for key, value in params.items():
        if isinstance(value, dict):
            processed_params[key] = json.dumps(value)
        else:
            processed_params[key] = value
    return processed_params


@tool
def get_request(url: str, params: dict | None = None) -> dict:
    """
    Launch a GET request to the given URL with query parameters.

    Args:
        url (str): The URL to send the GET request to
        params (dict): Query parameters to include in the request. Encode them as objects.
    """
    processed_params = _process_params(params)

    try:
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
            return _fallback_html_processing(response.text)

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
        processed_params = _process_params(params)
        post_data = {**data} if data else {}
        response = requests.post(
            url,
            headers=base_headers | {"content-type": "application/json", "referer": url},
            json=post_data,
            params=processed_params,
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


@tool
def get_request_crawl4ai(
    url: str, params: dict | None = None, expect_html: bool = False
) -> dict:
    """
    Launch a GET request to the given URL with query parameters using crawl4ai for HTML processing.

    This function provides better content extraction for web pages compared to BeautifulSoup,
    especially for complex JavaScript-heavy pages.

    Args:
        url (str): The URL to send the GET request to
        params (dict): Query parameters to include in the request. Encode them as objects.
        expect_html (bool): Whether to expect HTML content in the response.
    """
    time.sleep(2)
    processed_params = _process_params(params)

    if expect_html:
        # Directly use crawl4ai for HTML content extraction
        full_url = url
        if processed_params:
            query_string = "&".join(f"{k}={v}" for k, v in processed_params.items())
            full_url = f"{url}?{query_string}"
        return get_markdown_using_crawl4ai(full_url)

    try:
        response = requests.get(
            url, headers=base_headers | {"referer": url}, params=processed_params
        )
        response.raise_for_status()

        # Try to parse as JSON first
        try:
            result = response.json()
            # Check for GraphQL-style errors in successful responses
            if isinstance(result, dict) and "errors" in result:
                return {"error": f"API returned errors: {result['errors']}"}
            return result
        except json.JSONDecodeError:
            # HTML content - use crawl4ai for better extraction
            return get_markdown_using_crawl4ai(url)

    except requests.exceptions.RequestException as e:
        error_msg = f"Error in GET request: {e}"
        return {"error": error_msg}


def _fallback_html_processing(
    html_content: str, include_script_data: bool = True
) -> dict:
    """Fallback HTML processing using BeautifulSoup (original method)"""
    # Parse HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract JSON data from script tags
    script_data = ""

    # Look for script tags with JSON data
    if include_script_data:
        for script in soup.find_all("script"):
            if "data-target=" in str(script):
                script_data += "\n" + str(script)

    result = {"content": markdownify(html_content)}
    if include_script_data:
        result["extracted_data"] = script_data

    return result
