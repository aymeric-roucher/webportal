"""
Auto-generated API client from HAR file.
This file contains functions to interact with the API endpoints.
"""

import requests
import json
from typing import Optional, Dict, Any

from smolagents import (
    ToolCallingAgent,
    tool,
)


@tool
def get_manifest_json():
    """
    GET /manifest.json

    Original URL: https://github.com/manifest.json
    """
    import requests

    # Base URL
    base_url = "https://github.com"

    # Build URL with path parameters
    url = base_url + "/manifest.json"

    # Headers
    headers = {
        "sec-ch-ua-platform": "macOS",
        "Referer": "https://github.com/numpy/numpy/actions",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec-ch-ua": 'Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138',
        "sec-ch-ua-mobile": "?0",
    }

    response = requests.get(url, headers=headers, params=params)

    return (
        response.json()
        if response.headers.get("content-type", "").startswith("application/json")
        else response.text
    )


@tool
def post_pull_request_review_decisions():
    """
    POST /pull_request_review_decisions

    Original URL: https://github.com/pull_request_review_decisions
    """
    import requests

    # Base URL
    base_url = "https://github.com"

    # Build URL with path parameters
    url = base_url + "/pull_request_review_decisions"

    # Headers
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
        "content-length": "3331",
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundarykk6od7RPowurGp55",
        "origin": "https://github.com",
        "priority": "u=1, i",
        "referer": "https://github.com/numpy/numpy/pulls",
        "sec-ch-ua": 'Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "x-fetch-nonce": "v2:1f14f89b-2b2c-a8ba-59bd-71a5a7da6e6b",
        "x-github-client-version": "af8b8db961ba78e3d23e4b92e239c190ef136f06",
        "x-requested-with": "XMLHttpRequest",
    }

    response = requests.post(url, headers=headers, params=params)

    return (
        response.json()
        if response.headers.get("content-type", "").startswith("application/json")
        else response.text
    )


# Example usage:
if __name__ == "__main__":
    # Example: Call the first API endpoint
    # Replace with actual parameters as needed
    pass
