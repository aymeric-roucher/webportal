from pathlib import Path

from smolagents.models import InferenceClientModel

from webportal.common import DATA_PATH
from webportal.get_interactive.convert_to_api_docs import (
    convert_interactive_elements_to_api_docs,
)
from webportal.get_interactive.network_capture import SeleniumNetworkCaptureAgent


def ingest_from_prompt(prompt: str, data_dir: Path, headless: bool = True) -> str:
    """Main function to run the conversion"""
    data_dir.mkdir(parents=True, exist_ok=True)
    input_file = data_dir / Path("raw_markdown.md")

    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-32B-Instruct",
        provider="auto",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(
        model=model,
        data_dir=str(data_dir),
        markdown_file_path=input_file,
        browser_headless=headless,
    )
    selenium_vision_agent.run(prompt)
    content = input_file.read_text()
    api_docs = convert_interactive_elements_to_api_docs(input_elements=content)
    return api_docs


def ingest_clickaround(website_url: str, data_dir: Path) -> str:
    return ingest_from_prompt(
        f"I want you to click on every button on the page {website_url}, if you changed page, you should go back to the previous page",
        data_dir,
    )


if __name__ == "__main__":
    prompt = """
According to github, when was Regression added to the oldest closed numpy.polynomial issue that has the Regression label in MM/DD/YY?
                              
Start by going to the numpy package page and then click on the Issues tab.
"""
    data_dir = DATA_PATH / "github"
    ingest_from_prompt(prompt, data_dir)
