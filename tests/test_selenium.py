import json

import pytest

from webportal.common import DATA_PATH, MOCK_REQUESTS_PATH, TEST_PATH
from webportal.get_interactive.network_capture import PlaywrightNetworkCaptureAgent
from webportal.get_interactive.playwright_agent import (
    InferenceClientModel,
    PlaywrightVisionAgent,
)


@pytest.mark.expensive
def test_run_playwright_agent():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    playwright_vision_agent = PlaywrightVisionAgent(model=model, data_dir="data")
    playwright_vision_agent.run("""
I want you to go to github.com, to look for the numpy package and click the button to see all of the labels. 

Then I want you to go back, and to sort the issues by oldest order
                                   
              """)

@pytest.mark.expensive
def test_run_playwright_network_capture_agent():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    playwright_vision_agent = PlaywrightNetworkCaptureAgent(model=model, data_dir="data")
    playwright_vision_agent.run("""
I want you to go to github.com, to look for the numpy package and click the button to see all of the labels. 

Then I want you to go back, and to sort the issues by oldest order
                            
              """)


def test_return_requests():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    playwright_vision_agent = PlaywrightNetworkCaptureAgent(
        model=model, data_dir="data", markdown_file_path=DATA_PATH / "empty_markdown.md", browser_headless=False
    )
    playwright_vision_agent.tools["open_url"]("https://github.com")
    input("Press Enter to continue...")
    playwright_vision_agent.capture_requests_callback()
    
test_return_requests()
        
def test_analysing_requests():
    html_requests = json.loads((MOCK_REQUESTS_PATH / "github_html.json").read_text())
    json_requests = json.loads((MOCK_REQUESTS_PATH / "github_json.json").read_text())

    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    playwright_vision_agent = PlaywrightNetworkCaptureAgent(model=model, data_dir="data")

    markdown = playwright_vision_agent._generate_step_markdown(
        tool_call_info={
            "tool_name": "open_url",
            "arguments": {"url": "https://github.com"},
        },
        json_requests=json_requests,
        html_requests=html_requests,
    )
    (TEST_PATH / "markdown.md").write_text(markdown)
