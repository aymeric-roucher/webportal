from pathlib import Path


def create_conversion_prompt(content: str) -> str:
    """Create a detailed prompt for the LLM to convert the content"""
    
    example_format = '''```interactive_element_sort_oldest
location_page: numpy/numpy/issues
type: Button/Dropdown  
visual_element: Sort dropdown button with "Oldest" option in the issues list header
trigger: Click on sort dropdown and select "Oldest"
example:
result = get_request(https://github.com/_graphql, {
    "body": {
        "query": "22d008b451590c967cc8d672452db3f9",
        "variables": {
            "includeReactions": False,
            "name": "numpy",
            "owner": "numpy",
            "query": "is:issue state:open label:\"00 - Bug\" repo:numpy/numpy sort:created-desc",
            "skip": 0
        }
    }
})
effect: Sorts the issues list by creation date in ascending order (oldest first)
returns: JSON with paginated issues data sorted by oldest creation date first
viewport_effect: Updates the issues list display to show issues sorted chronologically from oldest to newest
```'''
    
    return f"""You are an expert API documentation generator. Your task is to convert raw interactive elements data from a website crawler into clean, structured API documentation.

INPUT FORMAT: The input contains step-by-step agent actions with captured network requests in this format:
- Agent output sections showing what the agent was doing
- Route sections showing captured API calls with basic information

OUTPUT FORMAT: Convert this into structured interactive elements with the following format:
{example_format}

CRITICAL INSTRUCTIONS:

There are 2 types of requests:
- GET requests
- POST requests

You will directly give an example using one of the two tools:
get_request or post_request.

1. **REMOVE USELESS ROUTES**: Filter out routes that are not useful for API documentation:
   - Static asset requests (CSS, JS, images)
   - Duplicate or redundant requests  
   - Internal tracking/analytics calls
   - One-time setup requests
   - Requests that don't provide meaningful functionality

2. **DO NOT GENERALIZE**:
   - Keep all specific values as they are.
   - Example: "numpy/numpy" should remain "numpy/numpy".
   - Do not replace values with variables like `^owner` or `^repo_name`.

3. **INFER MISSING INFORMATION**:
   - Add logical `type` (Button, Dropdown, Link, etc.)
   - Add descriptive `visual_element` based on context
   - Add clear `trigger` description based on agent actions
   - Add meaningful `effect` explaining what the API call accomplishes
   - Add `viewport_effect` describing UI changes

4. **STRUCTURE AND ORGANIZE**:
   - Group related functionality together
   - Use clear, descriptive names for interactive elements
   - Ensure each element is self-contained and reusable
   - You can add any additional information that you think is relevant to the API call

5. **MAINTAIN TECHNICAL ACCURACY**:
   - Keep all actual API endpoints, methods, and parameters intact
   - Preserve JSON structure in arguments
   - Don't modify GraphQL query hashes
   - Keep response format descriptions accurate

INPUT TO CONVERT:
{content}

Generate clean, structured API documentation following the format above. Focus on creating reusable, specific interactive elements that would be useful for an LLM to understand GitHub's API patterns."""


def call_llm(prompt: str) -> str:
    """Call GPT-4o via OpenAI API"""
    import os
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent output
            max_tokens=8000,  # Generous token limit for full conversion
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"OpenAI API call failed: {e}")


def convert_interactive_elements_to_api_docs(
    input_file: str | Path, 
    output_file: str | Path
) -> None:
    """Convert interactive_elements.md to structured API documentation"""
    
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    # Read the input file
    content = input_path.read_text()
    
    # Create the prompt for LLM processing
    prompt = create_conversion_prompt(content)
    
    # Call the LLM
    api_docs = call_llm(prompt)
    
    # Save the result
    output_path.write_text(api_docs)
    print(f"✅ Converted API documentation saved to: {output_path}")
