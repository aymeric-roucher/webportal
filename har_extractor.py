import json
import re
from urllib.parse import urlparse, parse_qs
import os


def _safe_json_parse(text):
    """Safely parse JSON text, returning None if parsing fails."""
    if not text or not text.strip():
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def extract_api_info(har_file_path):
    with open(har_file_path, 'r') as f:
        har = json.load(f)
    
    api_calls = {}
    
    for entry in har['log']['entries']:
        request = entry['request']
        response = entry['response']
        
        # Skip non-API calls (images, css, etc)
        content_type = response.get('content', {}).get('mimeType', '')
        if not ('json' in content_type or 'xml' in content_type):
            continue
            
        # Create endpoint pattern (replace IDs with placeholders)
        url = request['url']
        path = urlparse(url).path
        # Replace common ID patterns
        path_pattern = re.sub(r'/\d+', '/{id}', path)
        path_pattern = re.sub(r'/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '/{uuid}', path_pattern)
        
        # Store unique endpoints
        key = f"{request['method']} {path_pattern}"
        if key not in api_calls:
            api_calls[key] = {
                'method': request['method'],
                'url': url,
                'path': path_pattern,
                'queryParams': parse_qs(urlparse(url).query),
                'requestHeaders': {h['name']: h['value'] for h in request.get('headers', [])},
                'requestBody': _safe_json_parse(request.get('postData', {}).get('text')) if request.get('postData') and request.get('postData', {}).get('text') else None,
                'responseStatus': response['status'],
                'responseBody': _safe_json_parse(response.get('content', {}).get('text')) if response.get('content') and response.get('content', {}).get('text') else None
            }
    
    return api_calls


if __name__ == "__main__":

    har_folder = "har_data"
    har_files = [f for f in os.listdir(har_folder) if f.endswith('.har')]

    print("Found HAR files:")
    for idx, fname in enumerate(har_files):
        print(f"{idx+1}: {fname}")

    if not har_files:
        print("No HAR files found in the 'har_data' folder.")
        exit(1)

    try:
        file_choice = input("Enter the number of the HAR file to process: ")
        if not file_choice.strip():
            print("No input provided. Using first file.")
            file_idx = 0
            har_file_path = os.path.join(har_folder, har_files[file_idx])
        else:
            file_idx = int(file_choice) - 1
            har_file_path = os.path.join(har_folder, har_files[file_idx])
    except (ValueError, IndexError):
        print("Invalid selection.")
        exit(1)
    except EOFError:
        print("No input provided. Using first file.")
        file_idx = 0
        har_file_path = os.path.join(har_folder, har_files[file_idx])

    api_info = extract_api_info(har_file_path)

    try:
        output_path = input("Enter output file path (e.g., output.json): ").strip()
        if not output_path:
            output_path = "api_info.json"
    except EOFError:
        output_path = "api_info.json"
        print(f"Using default output file: {output_path}")

    output_path = os.path.join("./api_json", output_path)
    with open(output_path, "w") as out_f:
        json.dump(api_info, out_f, indent=2)

    print(f"API info extracted and saved to {output_path}")
