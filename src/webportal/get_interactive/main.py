from pathlib import Path
from webportal.common import WEBPORTAL_REPO_PATH, DATA_PATH
from webportal.get_interactive.convert_to_api_docs import convert_interactive_elements_to_api_docs
from webportal.get_interactive.network_capture import SeleniumNetworkCaptureAgent
from smolagents.models import InferenceClientModel


def main_crawl_website_and_get_markdown(prompt: str, data_dir: Path, headless: bool = True) -> Path:
    """Main function to run the conversion"""
    data_dir.mkdir(parents=True, exist_ok=True)
    input_file = data_dir / Path("raw_markdown.md")

    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(model=model, data_dir=str(data_dir), markdown_file_path=input_file, browser_headless=headless)
    selenium_vision_agent.run(prompt)

    # Set up paths
    output_file = input_file.with_name("digested_markdown")
    
    # Run conversion
    convert_interactive_elements_to_api_docs(
        input_file=input_file,
        output_file=output_file, 
    )
    
    return output_file

def click_on_every_button_on_the_page(website_url: str, data_dir: Path) -> Path:
    main_crawl_website_and_get_markdown(f"I want you to click on every button on the page {website_url}, if you changed page, you should go back to the previous page", data_dir)


if __name__ == "__main__":
    prompt = """
According to github, when was Regression added to the oldest closed numpy.polynomial issue that has the Regression label in MM/DD/YY?
                              
Start by going to the numpy package page and then click on the Issues tab.
"""
    data_dir = DATA_PATH / "github"
    main_crawl_website_and_get_markdown(prompt, data_dir)