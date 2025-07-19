import ast


def get_function_names(file_path):
    """
    Get the function names from a Python file.

    Args:
        file_path: The path to the Python file.

    Returns:
        A list of function names.
    """
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

# Example usage
print(get_function_names("./api_tools/test.py"))

