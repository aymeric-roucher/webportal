from pathlib import Path
from webportal.common import WEBPORTAL_REPO_PATH, DATA_PATH
from webportal.get_interactive.convert_to_api_docs import convert_interactive_elements_to_api_docs
from webportal.get_interactive.network_capture import SeleniumNetworkCaptureAgent
from smolagents.models import InferenceClientModel


def main_crawl_website_and_get_markdown(prompt: str, data_dir: Path) -> Path:
    """Main function to run the conversion"""
    
    input_file = WEBPORTAL_REPO_PATH / Path("digested_websites/interactive_elements.md")

    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(model=model, data_dir=str(data_dir), markdown_file_path=input_file)
    selenium_vision_agent.run(prompt)

    # Set up paths
    output_file = WEBPORTAL_REPO_PATH / Path("digested_websites/github_generated.md")
    
    # Run conversion
    convert_interactive_elements_to_api_docs(
        input_file=input_file,
        output_file=output_file, 
    )
    
    return output_file


if __name__ == "__main__":
    prompt = """
According to github, when was Regression added to the oldest closed numpy.polynomial issue that has the Regression label in MM/DD/YY?
                              
Start by going to the numpy package page and then click on the Issues tab.
"""
    data_dir = DATA_PATH
    main_crawl_website_and_get_markdown(prompt, data_dir)