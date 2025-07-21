import pytest
from webportal.get_interactive.selenium_agent import SeleniumVisionAgent, InferenceClientModel

@pytest.mark.expensive
def test_run_selenium_agent():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumVisionAgent(model=model, data_dir="data")
    selenium_vision_agent.run("""
I want you to go to github.com, to look for the numpy package and click the button to see all of the labels. 
              
When you are done, I want you to give me a list of the requests that were made to the server. 
              
              """)


def test_return_requests():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumVisionAgent(model=model, data_dir="data")
    selenium_vision_agent.tools["open_url"]("https://github.com/numpy/numpy/issues")
    selenium_vision_agent.tools["get_network_requests"]()