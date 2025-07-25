from pathlib import Path
from webportal.common import WEBPORTAL_REPO_PATH
from webportal.get_interactive.convert_to_api_docs import convert_interactive_elements_to_api_docs
from webportal.get_interactive.network_capture import SeleniumNetworkCaptureAgent
from smolagents.models import InferenceClientModel


def main():
    """Main function to run the conversion"""
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(model=model, data_dir="data")
    selenium_vision_agent.run("""
I want you to go to github.com, navigate to the numpy package, and perform the following actions to extract all interactive elements:

- Go to the issues page (numpy/numpy/issues)
- Click on the "Author" filter button to load author suggestions
- Click on the "Labels" filter button to see all available labels with their colors and descriptions.
- Click on the "Closed" button to toggle and view closed issues
- Use the sort dropdown to sort issues by "Oldest" order (creation date ascending)
Make sure to interact with each element completely to capture all the network requests and API calls that these interactive elements generate.
              """)


    # Set up paths
    input_file = WEBPORTAL_REPO_PATH / Path("data/interactive_elements.md")
    output_file = WEBPORTAL_REPO_PATH / Path("digested_websites/github_generated.md")
    
    # Run conversion
    convert_interactive_elements_to_api_docs(
        input_file=input_file,
        output_file=output_file, 
    )


if __name__ == "__main__":
    main()