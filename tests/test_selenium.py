import pytest
from webportal.get_interactive.selenium_agent import (
    SeleniumVisionAgent,
    InferenceClientModel,
)
from webportal.get_interactive.network_capture import SeleniumNetworkCaptureAgent
from time import sleep


@pytest.mark.expensive
def test_run_selenium_agent():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumVisionAgent(model=model, data_dir="data")
    selenium_vision_agent.run("""
I want you to go to github.com, to look for the numpy package and click the button to see all of the labels. 

Then I want you to go back, and to sort the issues by oldest order
                            
              """)


@pytest.mark.expensive
def test_run_selenium_network_capture_agent():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(model=model, data_dir="data")
    selenium_vision_agent.run("""
I want you to go to github.com, to look for the numpy package and click the button to see all of the labels. 

Then I want you to go back, and to sort the issues by oldest order
                            
              """)


test_run_selenium_network_capture_agent()


def test_return_requests():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumNetworkCaptureAgent(model=model, data_dir="data")
    selenium_vision_agent.tools["open_url"]("https://github.com")
    input("Press Enter to continue...")
    selenium_vision_agent.capture_requests_callback()
