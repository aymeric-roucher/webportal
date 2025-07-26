import pytest
from webportal.get_interactive.request_tools import get_request, post_request


@pytest.mark.expensive
def test_github_sponsor_batch_deferred():
    """Test GitHub sponsor batch deferred buttons POST request"""
    url = "https://github.com/sponsors/batch_deferred_sponsor_buttons"
    
    # This typically requires form data, testing with empty data
    result = post_request(url, {})
    
    # Expected to return JSON with sponsor button information or auth error
    assert ("error" in result or 
            "data" in result or 
            "item-" in str(result))


@pytest.mark.expensive  
def test_github_latest_commit_main():
    """Test GitHub latest commit for main branch"""
    url = "https://github.com/numpy/numpy/latest-commit/main"
    
    result = get_request(url)
    
    # Should return JSON with commit information
    assert "error" not in result or "oid" in str(result)
    if "error" not in result:
        # Verify expected commit keys are present
        expected_keys = ["oid", "url", "date", "shortMessageHtmlLink", "author"]
        content_str = str(result)
        assert any(key in content_str for key in expected_keys)


@pytest.mark.expensive
def test_github_refs_branch():
    """Test GitHub refs endpoint for branches"""
    url = "https://github.com/numpy/numpy/refs"
    params = {"type": "branch"}
    
    result = get_request(url, params)
    
    # Should return JSON with refs and cacheKey
    assert "error" not in result or "refs" in str(result)
    if "error" not in result:
        content_str = str(result)
        assert "refs" in content_str or "cacheKey" in content_str


@pytest.mark.expensive
def test_github_tree_commit_info():
    """Test GitHub tree commit info for main branch"""
    url = "https://github.com/numpy/numpy/tree-commit-info/main"
    
    result = get_request(url)
    
    # Should return JSON with file/directory information
    assert "error" not in result or "github" in str(result).lower()
    if "error" not in result:
        content_str = str(result).lower()
        # Look for common numpy directory/file names
        expected_items = [".github", "doc", "numpy", "readme", "license"]
        assert any(item in content_str for item in expected_items)


@pytest.mark.expensive
def test_github_overview_files():
    """Test GitHub overview files for main branch"""
    url = "https://github.com/numpy/numpy/overview-files/main"
    
    result = get_request(url)
    
    # Should return JSON with files and processingTime
    assert "error" not in result or "files" in str(result)
    if "error" not in result:
        content_str = str(result)
        assert "files" in content_str or "processingTime" in content_str


@pytest.mark.expensive
def test_github_branch_and_tag_count():
    """Test GitHub branch and tag count"""
    url = "https://github.com/numpy/numpy/branch-and-tag-count"
    
    result = get_request(url)
    
    # Should return JSON with branches and tags counts
    assert "error" not in result or "branches" in str(result)
    if "error" not in result:
        content_str = str(result)
        assert "branches" in content_str or "tags" in content_str


@pytest.mark.expensive
def test_github_label_validate():
    """Test GitHub label validation endpoint"""
    url = "https://github.com/_filter/labels/validate"
    params = {
        "repo": "numpy/numpy",
        "q": "00 - Bug", 
        "filter_value": "00 - Bug"
    }
    
    result = get_request(url, params)
    
    # Should return JSON with label information
    assert "error" not in result or "name" in str(result)
    if "error" not in result:
        content_str = str(result)
        expected_keys = ["name", "nameHtml", "description", "color"]
        assert any(key in content_str for key in expected_keys)


@pytest.mark.expensive
def test_github_search_repositories():
    """Test GitHub search for repositories"""
    url = "https://github.com/search"
    params = {
        "q": "numpy",
        "type": "repositories"
    }
    
    result = get_request(url, params)
    
    # Should return HTML page content
    assert "error" not in result
    if "content" in result:
        content_lower = result["content"].lower()
        assert "numpy" in content_lower
        assert ("repositories" in content_lower or "repository" in content_lower)


@pytest.mark.expensive
def test_github_numpy_repository_page():
    """Test GitHub numpy repository main page"""
    url = "https://github.com/numpy/numpy"
    
    result = get_request(url)
    
    # Should return HTML page content
    assert "error" not in result
    if "content" in result:
        content_lower = result["content"].lower()
        assert "numpy" in content_lower
        # Should contain typical repository page elements
        expected_elements = ["issues", "pull requests", "commits", "readme"]
        assert any(element in content_lower for element in expected_elements)


@pytest.mark.expensive
def test_github_numpy_issues_page():
    """Test GitHub numpy issues page"""
    url = "https://github.com/numpy/numpy/issues"
    
    result = get_request(url)
    
    # Should return HTML page content
    assert "error" not in result
    if "content" in result:
        content_lower = result["content"].lower()
        assert ("issues" in content_lower or "issue" in content_lower)
        # Should contain typical issues page elements
        expected_elements = ["open", "closed", "labels", "assignees"]
        assert any(element in content_lower for element in expected_elements)


@pytest.mark.expensive
def test_github_filtered_issues_page():
    """Test GitHub filtered issues page with bug label"""
    url = "https://github.com/numpy/numpy/issues"
    params = {
        "q": "is:issue state:open label:\"00 - Bug\" sort:created-asc"
    }
    
    result = get_request(url, params)
    
    # Should return HTML page content with filtered results
    assert "error" not in result
    if "content" in result:
        content_lower = result["content"].lower()
        assert "issues" in content_lower or "issue" in content_lower
        # May contain bug-related content or filter indicators
        filter_indicators = ["filter", "label", "bug", "open"]
        assert any(indicator in content_lower for indicator in filter_indicators)


@pytest.mark.expensive
def test_invalid_repository_endpoint():
    """Test handling of invalid repository endpoint"""
    url = "https://github.com/nonexistent-user/nonexistent-repo/latest-commit/main"
    
    result = get_request(url)
    
    # Should handle error gracefully
    assert ("error" in result or 
            "404" in str(result) or 
            "not found" in str(result).lower())


@pytest.mark.expensive  
def test_post_request_without_auth():
    """Test POST request that requires authentication"""
    url = "https://github.com/sponsors/batch_deferred_sponsor_buttons"
    
    # Test with various data formats
    test_data = {"test": "data"}
    result = post_request(url, test_data)
    
    # Should return an error or auth-related response
    assert ("error" in result or 
            "unauthorized" in str(result).lower() or
            "login" in str(result).lower() or
            "auth" in str(result).lower())


@pytest.mark.expensive
def test_github_repository_api_endpoints_error_handling():
    """Test error handling for repository API endpoints"""
    base_url = "https://github.com/nonexistent-user/nonexistent-repo"
    endpoints = [
        "/latest-commit/main",
        "/refs",
        "/tree-commit-info/main", 
        "/overview-files/main",
        "/branch-and-tag-count"
    ]
    
    for endpoint in endpoints:
        url = base_url + endpoint
        result = get_request(url)
        
        # All should handle errors gracefully
        assert ("error" in result or 
                "404" in str(result) or
                "not found" in str(result).lower())