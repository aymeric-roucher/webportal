import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse


def sanitize_function_name(endpoint):
    """Convert endpoint to a valid Python function name."""
    # Remove method and clean up the path
    method, path = endpoint.split(' ', 1)
    
    # Remove leading slash and replace special characters
    path = path.lstrip('/')
    path = re.sub(r'[^a-zA-Z0-9_]', '_', path)
    
    # Convert to lowercase and ensure it starts with a letter
    func_name = f"{method.lower()}_{path}".lower()
    if not func_name[0].isalpha():
        func_name = f"api_{func_name}"
    
    return func_name


def extract_path_parameters(path):
    """Extract parameters from path patterns like /{id} or /{uuid}."""
    params = []
    matches = re.findall(r'\{(\w+)\}', path)
    return matches


def generate_function_code(endpoint, api_info):
    """Generate Python function code for an API endpoint."""
    method = api_info['method']
    url = api_info['url']
    path = api_info['path']
    query_params = api_info['queryParams']
    headers = api_info['requestHeaders']
    request_body = api_info['requestBody']
    
    # Extract path parameters
    path_params = extract_path_parameters(path)
    
    # Generate function signature
    params = []
    if path_params:
        params.extend(path_params)
    if query_params:
        params.extend(query_params.keys())
    if request_body and isinstance(request_body, dict):
        params.extend(request_body.keys())
    
    # Remove duplicates and filter out None values
    params = list(set([p for p in params if p]))
    
    func_name = sanitize_function_name(endpoint)
    
    # Generate function code
    code = f"""
def {func_name}({', '.join(params) if params else ''}):
    \"\"\"
    {method} {path}
    
    Original URL: {url}
    \"\"\"
    import requests
    
    # Base URL
    base_url = "{urlparse(url).scheme}://{urlparse(url).netloc}"
    
    # Build URL with path parameters
    url = base_url + "{path}"
"""
    
    # Add path parameter substitution
    for param in path_params:
        code += f"    url = url.replace('{{{param}}}', str({param}))\n"
    
    # Add query parameters
    if query_params:
        code += "\n    # Query parameters\n    params = {}\n"
        for param in query_params.keys():
            code += f"    if {param} is not None:\n        params['{param}'] = {param}\n"
        code += "    \n"
    
    # Add headers
    code += "\n    # Headers\n    headers = {\n"
    for header_name, header_value in headers.items():
        if not header_name.startswith(':'):  # Skip pseudo-headers
            # Clean up header value (remove quotes)
            clean_value = header_value.strip('"')
            code += f"        '{header_name}': '{clean_value}',\n"
    code += "    }\n"
    
    # Add request body
    if request_body and isinstance(request_body, dict):
        code += "\n    # Request body\n    data = {\n"
        for key, value in request_body.items():
            code += f"        '{key}': {key},\n"
        code += "    }\n"
        code += "    \n"
        code += f"    response = requests.{method.lower()}(url, headers=headers, params=params, json=data)\n"
    else:
        code += f"\n    response = requests.{method.lower()}(url, headers=headers, params=params)\n"
    
    code += """
    return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
"""
    
    return code


def convert_json_to_python(json_file_path, output_file_path):
    """Convert API JSON file to Python script."""
    with open(json_file_path, 'r') as f:
        api_data = json.load(f)
    
    # Generate Python code
    python_code = '''"""
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

'''
    
    # Generate function for each API endpoint
    for endpoint, api_info in api_data.items():
        function_code = generate_function_code(endpoint, api_info)
        python_code += "\n"
        python_code += "@tool"
        python_code += function_code + "\n"
    
    # Add example usage
    python_code += '''
# Example usage:
if __name__ == "__main__":
    # Example: Call the first API endpoint
    # Replace with actual parameters as needed
    pass
'''
    
    # Write to file
    with open(output_file_path, 'w') as f:
        f.write(python_code)
    
    print(f"Generated Python API client: {output_file_path}")
    print(f"Found {len(api_data)} API endpoints")


if __name__ == "__main__":
    
    # List available JSON files
    api_json_dir = "api_json"
    json_files = [f for f in os.listdir(api_json_dir) if f.endswith('.json')]
    
    if not json_files:
        print("No JSON files found in api_json directory.")
        exit(1)
    
    print("Available JSON files:")
    for idx, fname in enumerate(json_files):
        print(f"{idx+1}: {fname}")
    
    # Get user choice
    try:
        choice = input("Enter the number of the JSON file to convert: ").strip()
        if not choice:
            choice = "1"
        file_idx = int(choice) - 1
        selected_file = json_files[file_idx]
    except (ValueError, IndexError):
        print("Invalid selection. Using first file.")
        selected_file = json_files[0]
    
    # Get output filename
    output_name = input("Enter output Python file name (e.g., github_api.py): ").strip()
    if not output_name:
        # Generate name from JSON file
        base_name = os.path.splitext(selected_file)[0]
        output_name = f"{base_name}_api.py"
    
    # Ensure .py extension
    if not output_name.endswith('.py'):
        output_name += '.py'
    
    output_name = os.path.join("./api_tools", output_name)

    # Convert the file
    json_path = os.path.join(api_json_dir, selected_file)
    convert_json_to_python(json_path, output_name) 
