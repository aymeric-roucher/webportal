from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from smolagents import (
    LocalPythonExecutor,
    OpenAIModel,
    ToolCallingAgent,
    tool,
)
from smolagents.local_python_executor import BASE_PYTHON_TOOLS

# from utils import get_function_names
from tools import get_manifest_json, post_pull_request_review_decisions
from tools_test import get_branch_and_tag_count_simple

load_dotenv()

model = OpenAIModel(model_id="gpt-3.5-turbo")  # "gpt-4o" for performance, "gpt-3.5-turbo" for testing

instructions = """
# Web Task Automation Agent

You are an advanced web automation agent specialized in performing complex tasks through API interactions. 
You reverse-engineer and interact with web services by analyzing their API patterns and executing precise HTTP requests.


You can:
- Execute sequential API calls with proper data flow between requests (important: you are given tools to do this)
- Handle pagination, rate limiting, and error recovery
- Extract and transform data between different API formats


When given a task, first:
- **Decompose** the task into atomic operations
- **Identify** required API endpoints and their dependencies
- **Map** the data flow between operations

"""


agent = ToolCallingAgent(
    model=model,
    # tools=[get_manifest_json, post_pull_request_review_decisions],
    tools=[get_branch_and_tag_count_simple],
    instructions=instructions,
)


task = f"""
You should answer the following question:

how many pull bramch and tags are there in the GitHub of numpy? (https://github.com/numpy/numpy/)
"""


agent.run(task)
