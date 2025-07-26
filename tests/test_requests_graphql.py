import pytest

from webportal.get_interactive.request_tools import get_request


@pytest.mark.expensive
def test_github_graphql_issue_search_archived():
    """Test GitHub GraphQL query for issue search with archived filter"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "29746fd23262d23f528e1f5b9b427437",
            "variables": {
                "name": "numpy",
                "owner": "numpy",
                "query": "is:issue archived:false repo:numpy/numpy sort:created-desc",
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_nodes_query():
    """Test GitHub GraphQL query for specific nodes"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "94d38dded736cdabaf92c2e06e57dc3e",
            "variables": {
                "includeReactions": False,
                "nodes": [
                    "I_kwDOAA3dP87CeS9R",
                    "I_kwDOAA3dP87B-PUE",
                    "I_kwDOAA3dP87B9gZ8",
                    "I_kwDOAA3dP87B9Lh1",
                    "I_kwDOAA3dP87BzbQL",
                ],
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_labels_query():
    """Test GitHub GraphQL query for labels without names"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "b480cbd1d6d3f7ba4a98229e88acf3fd",
            "variables": {
                "count": 100,
                "labelNames": "",
                "owner": "numpy",
                "repo": "numpy",
                "shouldQueryByNames": False,
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_bug_label_search():
    """Test GitHub GraphQL query for bug label search"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "22d008b451590c967cc8d672452db3f9",
            "variables": {
                "includeReactions": False,
                "name": "numpy",
                "owner": "numpy",
                "query": 'is:issue state:open label:"00 - Bug" repo:numpy/numpy sort:created-desc',
                "skip": 0,
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_bug_label_search_ascending():
    """Test GitHub GraphQL query for bug label search with ascending sort"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "22d008b451590c967cc8d672452db3f9",
            "variables": {
                "includeReactions": False,
                "name": "numpy",
                "owner": "numpy",
                "query": 'is:issue state:open label:"00 - Bug" sort:created-asc repo:numpy/numpy',
                "skip": 0,
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_labels_with_names():
    """Test GitHub GraphQL query for labels with specific names"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "b480cbd1d6d3f7ba4a98229e88acf3fd",
            "variables": {
                "count": 100,
                "labelNames": '"00 - Bug"',
                "owner": "numpy",
                "repo": "numpy",
                "shouldQueryByNames": True,
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_author_capabilities():
    """Test GitHub GraphQL query for author capabilities"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "76143934e91fc5d431ea7b83f63b08b9",
            "variables": {
                "capabilities": [],
                "first": 30,
                "loginNames": None,
                "name": "numpy",
                "owner": "numpy",
                "query": "",
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_issue_search_no_label():
    """Test GitHub GraphQL issue search without label filter"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "29746fd23262d23f528e1f5b9b427437",
            "variables": {
                "name": "numpy",
                "owner": "numpy",
                "query": 'is:issue state:open label:"00 - Bug" repo:numpy/numpy sort:created-desc',
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_issue_search_ascending_sort():
    """Test GitHub GraphQL issue search with ascending sort"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "29746fd23262d23f528e1f5b9b427437",
            "variables": {
                "name": "numpy",
                "owner": "numpy",
                "query": 'is:issue state:open label:"00 - Bug" sort:created-asc repo:numpy/numpy',
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_nodes_with_legacy_ids():
    """Test GitHub GraphQL query for nodes with legacy IDs"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "94d38dded736cdabaf92c2e06e57dc3e",
            "variables": {
                "includeReactions": False,
                "nodes": [
                    "MDU6SXNzdWU1OTAyNTUx",
                    "MDU6SXNzdWU2MzA4MTIy",
                    "MDU6SXNzdWU3NzE4NjUw",
                    "MDU6SXNzdWU3NzE4Njgw",
                    "MDU6SXNzdWU3NzIzOTkz",
                ],
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")


@pytest.mark.expensive
def test_github_graphql_extended_nodes_query():
    """Test GitHub GraphQL query for extended set of nodes"""
    url = "https://github.com/_graphql"

    query_data = {
        "body": {
            "query": "94d38dded736cdabaf92c2e06e57dc3e",
            "variables": {
                "includeReactions": False,
                "nodes": [
                    "I_kwDOAA3dP87CeS9R",
                    "I_kwDOAA3dP87B9gZ8",
                    "I_kwDOAA3dP87B9Lh1",
                    "I_kwDOAA3dP87BGb_Z",
                    "I_kwDOAA3dP87A9ZPS",
                    "I_kwDOAA3dP86_lHb1",
                    "I_kwDOAA3dP86_buBy",
                    "I_kwDOAA3dP86_XVnG",
                    "I_kwDOAA3dP86-xDnl",
                    "I_kwDOAA3dP86-PtAa",
                ],
            },
        }
    }

    result = get_request(url, query_data)
    assert "error" not in result or "API returned errors" in result.get("error", "")
