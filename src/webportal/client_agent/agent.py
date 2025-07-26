from dotenv import load_dotenv
from smolagents import (
    CodeAgent,
    OpenAIModel,
)

from webportal.common import WEBPORTAL_REPO_PATH
from webportal.get_interactive.request_tools import get_request, post_request

load_dotenv()

model = OpenAIModel(
    model_id="gpt-4.1"  # for 200k token per minute
)


with open(WEBPORTAL_REPO_PATH / "digested_websites/github_generated.md", "r") as f:
    interaction_description = f.read()

instructions = f"""
# Web Task Automation Agent

You are an advanced web automation agent specialized in performing complex tasks through API interactions. 

Below is a description of the API calls that you can make to the desired domain.
You cannot use them directly, you need to use the tools provided to you.

We used a crawler to extract the following API calls:
{interaction_description}

"""

if __name__ == "__main__":
    agent = CodeAgent(
        model=model,
        tools=[get_request, post_request],
        instructions=instructions,
        additional_authorized_imports=["urllib.*"],
        verbosity_level=2,
    )

    task = "According to github, when was Regression added to the oldest closed numpy.polynomial issue that has the Regression label in MM/DD/YY?"

    agent.run(task)
