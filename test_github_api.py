#!/usr/bin/env python3
"""
Test GitHub GraphQL API call for fetching numpy issues
"""

import requests
import json
from urllib.parse import quote

def test_github_graphql_api():
    """Test the GitHub GraphQL API call for numpy issues."""
    
    # The API call from the HAR file
    url = "https://github.com/_graphql"
    
    # The query parameters from the HAR file
    query_params = {
        "body": json.dumps({
            "query": "29746fd23262d23f528e1f5b9b427437",
            "variables": {
                "name": "numpy",
                "owner": "numpy", 
                "query": "is:issue archived:false repo:numpy/numpy sort:created-desc"
            }
        })
    }
    
    # Headers that might be needed for GitHub API
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    
    print("Testing GitHub GraphQL API call...")
    print(f"URL: {url}")
    print(f"Query params: {json.dumps(query_params, indent=2)}")
    print()
    
    try:
        # Make the request
        response = requests.get(url, params=query_params, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            print("✅ API call successful!")
            try:
                data = response.json()
                print(f"Response data: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response text (not JSON): {response.text[:500]}...")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error making API call: {e}")

if __name__ == "__main__":
    test_github_graphql_api() 