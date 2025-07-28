from time import time
import json
from time import time
import pytest

from webportal.common import DATA_PATH, MOCK_REQUESTS_PATH, TEST_PATH
from webportal.get_interactive.network_capture import SeleniumNetworkCaptureAgent
from webportal.get_interactive.selenium_agent import (
    InferenceClientModel,
    SeleniumVisionAgent,
)



@pytest.mark.expensive
def test_run_selenium_agent():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-32B-Instruct",
        provider="auto",
    )
    selenium_vision_agent = SeleniumVisionAgent(model=model, data_dir="data", browser_headless=False,)
    selenium_vision_agent.run("""
I want you to go to github.com, to look for the numpy package and click the button to see all of the labels. 

Then I want you to go back, and to sort the issues by oldest order                            
              """)
    
    
@pytest.mark.expensive
def test_run_selenium_network_capture_agent():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-32B-Instruct",
        provider="auto",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(model=model, data_dir="data", browser_headless=True)
    selenium_vision_agent.run("""
I want you to go to github.com, to look for the numpy package and click the button to see all of the labels. 

Then I want you to go back, and to sort the issues by oldest order
                            
              """)


def test_return_requests(url: str = "github.com"):
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-32B-Instruct",
        provider="auto",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(
        model=model,
        data_dir="data",
        markdown_file_path=DATA_PATH / "empty_markdown.md",
        browser_headless=False,
    )
    selenium_vision_agent.tools["open_url"](url)
    input("Press Enter to continue...")
    from smolagents import ActionStep, Timing, ToolCall

    memory_step = ActionStep(
        0,
        Timing(start_time=time()),
        tool_calls=[ToolCall(name="open_url", arguments={"url": url}, id="1")],
    )
    selenium_vision_agent.capture_requests_callback(memory_step, selenium_vision_agent)
    
def test_analysing_requests():
    html_requests = json.loads((MOCK_REQUESTS_PATH / "github_html.json").read_text())
    json_requests = json.loads((MOCK_REQUESTS_PATH / "github_json.json").read_text())

    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-32B-Instruct",
        provider="auto",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(model=model, data_dir="data")

    markdown = selenium_vision_agent._generate_step_interaction_summary_markdown(
        tool_call_info={
            "tool_name": "open_url",
            "arguments": {"url": "https://github.com"},
        },
        json_requests=json_requests,
        html_requests=html_requests,
    )
    (TEST_PATH / "markdown.md").write_text(markdown)
