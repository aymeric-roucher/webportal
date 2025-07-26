import json


def describe_response_format(response_body: str) -> str:
    """Describe the format and content of the response. If the response is a JSON object, return the schema of the object."""
    if not response_body:
        return "Empty response"

    try:
        # Try to parse as JSON
        json_data = json.loads(response_body)
        if isinstance(json_data, dict):
            # Return the schema of the JSON object
            def get_schema(obj, depth=0, max_depth=3):
                if depth > max_depth:
                    return "..."
                if isinstance(obj, dict):
                    return {
                        k: get_schema(v, depth + 1, max_depth) for k, v in obj.items()
                    }
                elif isinstance(obj, list):
                    if obj:
                        return [get_schema(obj[0], depth + 1, max_depth)]
                    else:
                        return []
                else:
                    return type(obj).__name__

            schema = get_schema(json_data)
            return f"JSON schema:\n{json.dumps(schema, indent=2)}"
        elif isinstance(json_data, list):
            if len(json_data) > 0:
                # Get the schema of each element in the list (up to a reasonable number, e.g., 3)
                def get_schema(obj, depth=0, max_depth=3):
                    if depth > max_depth:
                        return "..."
                    if isinstance(obj, dict):
                        return {
                            k: get_schema(v, depth + 1, max_depth)
                            for k, v in obj.items()
                        }
                    elif isinstance(obj, list):
                        if obj:
                            return [get_schema(obj[0], depth + 1, max_depth)]
                        else:
                            return []
                    else:
                        return type(obj).__name__

                schemas = [get_schema(item) for item in json_data[:3]]
                return (
                    f"JSON array with {len(json_data)} items. "
                    f"Element schemas (first {min(3, len(json_data))}):\n"
                    f"{json.dumps(schemas, indent=2)}"
                )
            else:
                return "JSON array (empty)"
        else:
            return "JSON response"
    except json.JSONDecodeError:
        if "DOCTYPE" in response_body:
            return "HTML page content"
        else:
            return "Text/other format response"


def test_describe_response_format():
    response_body = """
    {
        "name": "John",
        "age": 30,
        "city": "New York"
    }
    """
    output = describe_response_format(response_body)
    assert (
        output
        == 'JSON schema:\n{\n  "name": "str",\n  "age": "int",\n  "city": "str"\n}'
    )

    response_body = """
    [
        {
            "name": "John",
            "age": 30,
            "city": "New York"
        }
    ]
    """
    output = describe_response_format(response_body)
    assert (
        output
        == 'JSON array with 1 items. Element schemas (first 1):\n[\n  {\n    "name": "str",\n    "age": "int",\n    "city": "str"\n  }\n]'
    )


if __name__ == "__main__":
    test_describe_response_format()
