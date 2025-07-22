import requests

from smolagents import (
    ToolCallingAgent,
    tool,
)


def get_numpy_pulse_committer_data():
    """
    Fetches the pulse committer data for the numpy/numpy repository from GitHub.

    Returns:
        list: A list of dictionaries containing committer information with fields:
            - name: Committer's name
            - login: GitHub username (can be None)
            - gravatar: URL to avatar image
            - commits: Number of commits
            - hovercard_url: URL for user hovercard (optional)

        Returns None if the request fails.
    """
    url = "https://github.com/numpy/numpy/pulse_committer_data"

    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
        "referer": "https://github.com/numpy/numpy/pulse",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching committer data: {e}")
        return None


def get_pull_request_review_decisions(pull_request_ids, authenticity_token=None):
    """
    Fetches review decisions for multiple pull requests from GitHub.

    Args:
        pull_request_ids (list): List of pull request IDs to check
        authenticity_token (str, optional): GitHub authenticity token for the session

    Returns:
        dict: A dictionary with keys like "item-0", "item-1", etc. containing
              HTML snippets for review status (empty string if no special status)

        Returns None if the request fails.
    """
    url = "https://github.com/pull_request_review_decisions"

    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
        "origin": "https://github.com",
        "referer": "https://github.com/numpy/numpy/pulls",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    # Prepare the multipart form data
    # Note: The actual form data structure wasn't provided in the HAR extract
    # This is a typical structure based on the endpoint name
    files = {
        "pull_request_ids[]": (None, ",".join(map(str, pull_request_ids))),
    }

    if authenticity_token:
        files["authenticity_token"] = (None, authenticity_token)

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching pull request review decisions: {e}")
        return None


def get_branch_and_tag_count(owner, repo):
    """
    Simple version that just gets the branch and tag counts.

    Args:
        owner (str): Repository owner
        repo (str): Repository name

    Returns:
        dict: {'branches': int, 'tags': int} or None if request fails
    """
    url = f"https://github.com/{owner}/{repo}/branch-and-tag-count"

    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
        "content-type": "application/json",
        "github-verified-fetch": "true",
        "referer": f"https://github.com/{owner}/{repo}",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching branch and tag count: {e}")
        return None


@tool
def get_branch_and_tag_count_simple():
    """
    Get the branch and tag count for the numpy/numpy repository.

    Returns:
        dict: {'branches': int, 'tags': int} or None if request fails
    """
    return get_branch_and_tag_count("numpy", "numpy")


# Example usage:
if __name__ == "__main__":
    committers = get_numpy_pulse_committer_data()
    if committers:
        print(f"Found {len(committers)} committers:")
        for committer in committers:
            print(
                f"- {committer['name']} ({committer.get('login', 'No login')}) - {committer['commits']} commits"
            )

    counts = get_branch_and_tag_count("numpy", "numpy")
    if counts:
        print(
            f"NumPy repository has {counts['branches']} branches and {counts['tags']} tags"
        )
