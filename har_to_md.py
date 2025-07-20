#!/usr/bin/env python3
"""
HAR to Markdown Converter

This script takes a HAR file and converts it to a markdown description
of all the API functions that can be called, matching the format of
files in the digested_websites directory.
"""

import json
import sys
import os
import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Optional


def extract_api_calls(har_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract API calls from HAR data."""
    api_calls = []
    unique_calls = {}  # Track unique API calls
    
    if 'log' not in har_data or 'entries' not in har_data['log']:
        return api_calls
    
    for entry in har_data['log']['entries']:
        request = entry.get('request', {})
        response = entry.get('response', {})
        
        # Skip non-API requests (images, CSS, JS, etc.)
        if not is_api_request(request):
            continue
        
        url = request.get('url', '')
        method = request.get('method', 'GET')
        
        # Create unique identifier for this API call
        # Use URL path and method as the key, ignoring query parameters for uniqueness
        parsed = urlparse(url)
        unique_key = f"{method}:{parsed.path}"
        
        # If we've already seen this API call, skip it
        if unique_key in unique_calls:
            continue
            
        api_call = {
            'method': method,
            'url': url,
            'headers': {h['name']: h['value'] for h in request.get('headers', [])},
            'postData': request.get('postData', {}),
            'status': response.get('status', 0),
            'responseHeaders': {h['name']: h['value'] for h in response.get('headers', [])}
        }
        
        api_calls.append(api_call)
        unique_calls[unique_key] = True  # Mark as seen
    
    return api_calls


def is_api_request(request: Dict[str, Any]) -> bool:
    """Determine if a request is an API call."""
    url = request.get('url', '').lower()
    method = request.get('method', 'GET').upper()
    
    # Skip static assets
    static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf']
    if any(url.endswith(ext) for ext in static_extensions):
        return False
    
    # Skip analytics and tracking
    if any(tracker in url for tracker in ['analytics', 'tracking', 'stats', 'telemetry']):
        return False
    
    # Look for API indicators
    api_indicators = [
        '/api/', '/graphql', '/_graphql', '/rest/', '/v1/', '/v2/', '/v3/',
        'api.github.com', 'api.twitter.com', 'api.slack.com'
    ]
    
    if any(indicator in url for indicator in api_indicators):
        return True
    
    # Consider POST/PUT/DELETE requests as potential API calls
    if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        return True
    
    # Check for JSON content type
    headers = {h['name'].lower(): h['value'] for h in request.get('headers', [])}
    content_type = headers.get('content-type', '')
    if 'application/json' in content_type:
        return True
    
    return False


def generate_element_name(url: str, method: str) -> str:
    """Generate a descriptive element name from URL and method."""
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')
    
    # Remove common prefixes
    if path_parts and path_parts[0] in ['api', 'v1', 'v2', 'v3', 'rest']:
        path_parts = path_parts[1:]
    
    # Create a descriptive name
    if len(path_parts) >= 2:
        resource = path_parts[-2] if path_parts[-1].isdigit() else path_parts[-1]
        action = method.lower()
        return f"{action}_{resource}"
    elif len(path_parts) == 1:
        return f"{method.lower()}_{path_parts[0]}"
    else:
        return f"{method.lower()}_endpoint"


def extract_arguments(request: Dict[str, Any]) -> Dict[str, Any]:
    """Extract arguments from the request."""
    args = {}
    
    # Extract query parameters
    url = request.get('url', '')
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    for key, values in query_params.items():
        args[key] = values[0] if len(values) == 1 else values
    
    # Extract POST data
    post_data = request.get('postData', {})
    if post_data:
        content_type = post_data.get('mimeType', '')
        if 'application/json' in content_type:
            try:
                json_data = json.loads(post_data.get('text', '{}'))
                args.update(json_data)
            except json.JSONDecodeError:
                pass
        elif 'application/x-www-form-urlencoded' in content_type:
            form_data = parse_qs(post_data.get('text', ''))
            for key, values in form_data.items():
                args[key] = values[0] if len(values) == 1 else values
    
    return args


def determine_visual_element(url: str, method: str) -> str:
    """Determine the visual element that triggers this API call."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    # Map common patterns to UI elements
    if 'graphql' in path:
        return "GraphQL query interface"
    elif 'search' in path or 'query' in path:
        return "Search input field"
    elif 'filter' in path:
        return "Filter dropdown or button"
    elif 'sort' in path:
        return "Sort dropdown"
    elif 'page' in path or 'pagination' in path:
        return "Pagination controls"
    elif 'hover' in path or 'hovercard' in path:
        return "Hover trigger on interactive elements"
    elif method == 'POST':
        return "Form submission or button click"
    elif method == 'DELETE':
        return "Delete button or action"
    elif method == 'PUT' or method == 'PATCH':
        return "Edit form or update button"
    else:
        return "Page navigation or link click"


def determine_effect(url: str, method: str) -> str:
    """Determine the effect of the API call."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if 'graphql' in path:
        return "Executes GraphQL query to fetch data"
    elif 'search' in path:
        return "Performs search operation"
    elif 'filter' in path:
        return "Applies filters to data"
    elif 'sort' in path:
        return "Sorts data by specified criteria"
    elif 'page' in path:
        return "Loads paginated data"
    elif 'hover' in path:
        return "Loads hover card data"
    elif method == 'POST':
        return "Creates or submits new data"
    elif method == 'DELETE':
        return "Removes or deletes data"
    elif method == 'PUT' or method == 'PATCH':
        return "Updates existing data"
    else:
        return "Fetches data from server"


def determine_viewport_effect(url: str, method: str) -> str:
    """Determine the viewport effect of the API call."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if 'hover' in path:
        return "Displays popup or tooltip"
    elif 'search' in path or 'filter' in path:
        return "Updates search results or filtered content"
    elif 'sort' in path:
        return "Reorders displayed content"
    elif 'page' in path:
        return "Loads new page of content"
    elif method == 'POST':
        return "Updates page content or shows success/error message"
    elif method == 'DELETE':
        return "Removes content from view"
    elif method == 'PUT' or method == 'PATCH':
        return "Updates displayed content"
    else:
        return "Updates page content"


def format_arguments(args: Dict[str, Any]) -> str:
    """Format arguments as a JSON-like string."""
    if not args:
        return "{}"
    
    # Format for readability
    formatted = json.dumps(args, indent=2)
    # Remove outer braces and indent
    lines = formatted.split('\n')
    if len(lines) > 1:
        return '{\n' + '\n'.join('  ' + line for line in lines[1:-1]) + '\n}'
    else:
        return formatted


def generate_markdown(api_calls: List[Dict[str, Any]], domain: str) -> str:
    """Generate markdown content from API calls."""
    if not api_calls:
        return "# No API calls found in HAR file\n\nThis HAR file doesn't contain any API calls that could be converted to interactive elements."
    
    markdown_lines = []
    
    for i, call in enumerate(api_calls):
        url = call['url']
        method = call['method']
        
        # Generate element name
        element_name = generate_element_name(url, method)
        
        # Extract arguments
        args = extract_arguments(call)
        
        # Determine UI elements
        visual_element = determine_visual_element(url, method)
        effect = determine_effect(url, method)
        viewport_effect = determine_viewport_effect(url, method)
        
        # Generate markdown block
        block = f"""```interactive_element_{element_name}
type: {method} request
visual_element: {visual_element}
trigger: User interaction (click, hover, form submission, etc.)
request: {method} {url}
arguments: {format_arguments(args)}
effect: {effect}
returns: JSON or HTML response data
viewport_effect: {viewport_effect}
```"""
        
        markdown_lines.append(block)
    
    return '\n\n'.join(markdown_lines)


def main():
    """Main function to process HAR file."""
    if len(sys.argv) != 2:
        print("Usage: python har_to_md.py <har_file>")
        print("Example: python har_to_md.py har_data/github.com.har")
        sys.exit(1)
    
    har_file = sys.argv[1]
    
    if not os.path.exists(har_file):
        print(f"Error: File '{har_file}' not found.")
        sys.exit(1)
    
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in HAR file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading HAR file: {e}")
        sys.exit(1)
    
    # Extract API calls
    api_calls = extract_api_calls(har_data)
    
    if not api_calls:
        print("No API calls found in the HAR file.")
        sys.exit(0)
    
    # Determine domain from first API call
    domain = urlparse(api_calls[0]['url']).netloc if api_calls else "unknown"
    
    # Generate markdown
    markdown_content = generate_markdown(api_calls, domain)
    
    # Create output filename
    base_name = os.path.splitext(os.path.basename(har_file))[0]
    output_file = f"{base_name}_api_calls.md"
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Generated {len(api_calls)} API call descriptions in '{output_file}'")
    print(f"Domain: {domain}")


if __name__ == "__main__":
    main() 