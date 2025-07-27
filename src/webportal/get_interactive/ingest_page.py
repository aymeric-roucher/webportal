import time
from pathlib import Path

from smolagents.models import InferenceClientModel

from webportal.common import DATA_PATH
from webportal.get_interactive.convert_to_api_docs import (
    convert_interactive_elements_to_api_docs,
)
from webportal.get_interactive.network_capture import SeleniumNetworkCaptureAgent

INGESTION_PROMPT = """
You are tasked with exploring all interactive elements of the following webpage: {target_url}
Your browser is already open at this initial page, and a screenshot is shown below.

Your aim is to find all interactions that have not been found by our crawler (this crawler just gathered all the link elements form the HTML).
So you should try to explore all nontrivial interactions : select all interesting options in a form, click page selection, enable filters, etc.
We will then intercept network requests made during interactions : so if you're interacting with a form for instance, make sure to submit it to trigger the request.
Clicking simple links is not useful, avoid it.

This will later be used to create a full functional graph from the website : so make sure to cover interactions that would be useful to common users.
Never bother exploring subpages of the initial page, because these will be explored by other agents, one per url : so once you've tried some interaction or your interactions brought you to a new page, you can use open_url to go back to the initial url, then explore other elements.
Go on ! Make sure to explore all the meaningful user interactions that one would expect to do from your starting page. A good rule of thumb is to try at least 3 different interaction flows.
Don't do too much planning.
When you're finished, return "I finished the exploration".
"""


def ingest_page(
    target_url: str,
    data_dir: Path,
    headless: bool = True,
    domain_to_stay_on: str | None = None,
    custom_prompt: str | None = None,
) -> str:
    """Main function to run the conversion"""
    data_dir.mkdir(parents=True, exist_ok=True)
    input_file = data_dir / Path("raw_markdown.md")

    ingestion_prompt = custom_prompt or INGESTION_PROMPT.format(target_url=target_url)

    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-32B-Instruct",
        provider="auto",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(
        model=model,
        data_dir=str(data_dir),
        markdown_file_path=input_file,
        browser_headless=headless,
        domain_to_stay_on=domain_to_stay_on,
        max_steps=20,
    )
    screenshot = selenium_vision_agent.quick_open_url(target_url)
    selenium_vision_agent.run(ingestion_prompt, images=[screenshot])
    selenium_vision_agent.close()  # Clean up browser resources
    content = input_file.read_text()
    api_docs = convert_interactive_elements_to_api_docs(input_elements=content)
    return api_docs


if __name__ == "__main__":
    data_dir = DATA_PATH / "github"
    ingest_page("github.com", data_dir)
