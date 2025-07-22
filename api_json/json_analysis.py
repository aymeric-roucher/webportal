import json
from collections import Counter


def count_unique_apis(json_path):
    """
    Counts the number of unique APIs in the given github2.json file.
    Uniqueness is determined by the combination of HTTP method and path.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    unique_apis = set()
    for api_key, api_info in data.items():
        # Try to get method and path from the value, else parse from the key
        method = api_info.get("method")
        path = api_info.get("path")
        if not method or not path:
            # Fallback: parse from key, e.g. "GET /foo/bar"
            try:
                method, path = api_key.split(" ", 1)
            except Exception:
                continue
        unique_apis.add((method.upper(), path))

    print(f"Number of unique APIs: {len(unique_apis)}")
    return len(unique_apis)


if __name__ == "__main__":
    # Adjust the path as needed
    count_unique_apis("github2.json")
