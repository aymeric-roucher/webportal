import os
import re

# def count_distinct_api_calls(md_file_path):
#     """
#     Counts the number of distinct API calls in a markdown file.
#     Assumes each API call is denoted by a code block starting with ```interactive_element_.
#     """
#     api_call_pattern = re.compile(r"^```interactive_element_", re.MULTILINE)
#     with open(md_file_path, "r", encoding="utf-8") as f:
#         content = f.read()
#     matches = api_call_pattern.findall(content)
#     return len(matches)

def count_api_calls_by_triple_backticks(md_file_path):
    """
    Counts the number of code blocks (delimited by ```) in a markdown file.
    Each code block is considered an API call.
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Find all occurrences of triple backticks
    triple_backtick_pattern = re.compile(r"^```", re.MULTILINE)
    matches = triple_backtick_pattern.findall(content)
    # Each code block has an opening and closing ```, so divide by 2
    return len(matches) // 2

def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    md_files = [f for f in os.listdir(folder) if f.endswith(".md")]
    if not md_files:
        print("No *_api_calls.md files found in this folder.")
        return

    for md_file in md_files:
        path = os.path.join(folder, md_file)
        count = count_api_calls_by_triple_backticks(path)
        print(f"{md_file}: {count} distinct API calls")

if __name__ == "__main__":
    main()

