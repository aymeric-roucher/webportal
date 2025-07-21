import os
import time
import unicodedata
import json
from datetime import datetime
from io import BytesIO
from typing import Any

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageDraw

# SmolaAgents imports
from smolagents import CodeAgent, tool
from smolagents.agent_types import AgentImage
from smolagents.memory import ActionStep, TaskStep
from smolagents.monitoring import LogLevel
from smolagents import InferenceClientModel

SELENIUM_SYSTEM_PROMPT_TEMPLATE = """You are a web automation assistant that can control a local browser using Selenium. The current date is <<current_date>>.

<action process>
You will be given a task to solve in several steps. At each step you will perform an action.
After each action, you'll receive an updated screenshot. 
Then you will proceed as follows, with these sections: don't skip any!

Short term goal: ...
What I see: ...
Reflection: ...
Action:
```python
click(254, 308)
```<end_code>

Akways format your action ('Action:' part) as Python code blocks as shown above.
</action_process>

<tools>
On top of performing computations in the Python code snippets that you create, you only have access to these tools to interact with the desktop, no additional ones:
{%- for tool in tools.values() %}
- {{ tool.name }}: {{ tool.description }}
    Takes inputs: {{tool.inputs}}
    Returns an output of type: {{tool.output_type}}
{%- endfor %}
</tools>

<click_guidelines>
Look at elements on the web page to determine what to click or interact with.
The browser window has a resolution of <<resolution_x>>x<<resolution_y>> pixels, take it into account to decide clicking coordinates. NEVER USE HYPOTHETIC OR ASSUMED COORDINATES, USE TRUE COORDINATES that you can see from the screenshot.
Use precise coordinates based on the current screenshot for mouse movements and clicks. 
Whenever you click, MAKE SURE to click in the middle of the button, text, link or any other clickable element. Not under, not on the side. IN THE MIDDLE, else you risk to miss it.
For web elements it is always better to click in the middle of the text rather than edges. Calculate extremely well the coordinates. A mistake here can make the full task fail.
Sometimes you may have missed a click, so never assume that you're on the right page, always make sure that your previous action worked.
In the screenshot you will see a green crosshair displayed over the position of your last click: this way can inspect if the mouse pointer is off of the targeted element, pay special attention to it.
</click_guidelines>

<task_resolution_example>
For a task like "Go to Google and search for 'Hello World'":
Step 1:
Short term goal: I want to open Google website.
What I see: I see the browser is open but no specific page is loaded yet.
Reflection: I need to navigate to Google first. I'll use the open_url tool to go directly to Google.
Action:
```python
open_url("https://google.com")
```<end_code>

Step 2:
Short term goal: I want to search for 'Hello World'.
What I see: I can see the Google homepage with the search box in the center of the page.
Reflection: I can see the Google search box. I need to click on it first and then type my search query.
Action:
```python
click(640, 360) 
```<end_code>

Step 3:
Short term goal: I want to type 'Hello World' in the search box.
What I see: The search box is now active with a cursor visible.
Reflection: The search box is ready for input. I'll type 'Hello World' now.
Action:
```python
type_text("Hello World")
```<end_code>

Step 4:
Short term goal: I want to submit the search.
What I see: I can see 'Hello World' typed in the search box and there's a search button or I can press Enter.
Reflection: I can either click the search button or press Enter to submit the search. I'll press Enter.
Action:
```python
press_key("enter")
```<end_code>

Step 5:
Short term goal: Verify the search results.
What I see: The Google search results page is showing results for 'Hello World'.
Reflection: Perfect! The search has been completed successfully. I can see search results for 'Hello World' are displayed.
Action:
```python
final_answer("Successfully searched for 'Hello World' on Google")
```<end_code>
</task_resolution_example>

<general_guidelines>
Always analyze the latest screenshot carefully before performing actions.
You can wait for appropriate loading times using the wait() tool. But don't wait forever, sometimes pages load slowly or elements need time to appear.
Execute one action at a time: don't try to pack a click and typing in one action.
On each step, look at the last screenshot and action to validate if previous steps worked and decide the next action. If you repeated an action already without effect, it means that this action is useless: don't repeat it and try something else.
Use click to interact with web elements and scroll to navigate through web pages.
Always analyze the latest screenshot carefully before performing actions.
Web pages may have dropdowns, modals, and interactive elements that appear on hover or click.
Use open_url to navigate to new websites directly.
In browser, ignore any sign-in popups, cookie banners, or ads while they don't interfere with the elements you want to interact with.
Wait for page elements to load before interacting with them.
</general_guidelines>
""".replace("<<current_date>>", datetime.now().strftime("%A, %d-%B-%Y"))


def draw_marker_on_image(image_copy, click_coordinates):
    x, y = click_coordinates
    draw = ImageDraw.Draw(image_copy)
    cross_size, linewidth = 10, 3
    # Draw cross
    draw.line((x - cross_size, y, x + cross_size, y), fill="green", width=linewidth)
    draw.line((x, y - cross_size, x, y + cross_size), fill="green", width=linewidth)
    # Add a circle around it for better visibility
    draw.ellipse(
        (
            x - cross_size * 2,
            y - cross_size * 2,
            x + cross_size * 2,
            y + cross_size * 2,
        ),
        outline="green",
        width=linewidth,
    )
    return image_copy


def get_agent_summary_erase_images(agent):
    for memory_step in agent.memory.steps:
        if hasattr(memory_step, "observations_images"):
            memory_step.observations_images = None
        if hasattr(memory_step, "task_images"):
            memory_step.task_images = None
    return agent.write_memory_to_messages()


class SeleniumVisionAgent(CodeAgent):
    """Agent for local browser automation with Selenium and Qwen2.5VL vision capabilities"""

    def __init__(
        self,
        model: InferenceClientModel,
        data_dir: str,
        tools: list[tool] = None,
        max_steps: int = 200,
        verbosity_level: LogLevel = 2,
        planning_interval: int = None,
        use_v1_prompt: bool = False,
        **kwargs,
    ):
        self.data_dir = data_dir
        self.planning_interval = planning_interval
        
        chrome_options = webdriver.ChromeOptions()
        self.width, self.height = 1080, 1920
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-pdf-viewer")
        chrome_options.add_argument("--window-position=0,0")
        # Enable Chrome DevTools Protocol for network monitoring
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--enable-network-service-logging")
        chrome_options.add_argument("--log-level=0")
        # Enable performance logs to capture network requests
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Initialize network request tracking
        self.network_requests = []
        self._setup_network_monitoring()
        
        # Set browser window size
        self.driver.set_window_size(self.width, self.height)
        print(f"Browser window size: {self.width}x{self.height}")

        # Set up temp directory
        os.makedirs(self.data_dir, exist_ok=True)
        print(f"Screenshots and steps will be saved to: {self.data_dir}")

        self.use_v1_prompt = use_v1_prompt
        # Initialize base agent
        super().__init__(
            tools=tools or [],
            model=model,
            max_steps=max_steps,
            verbosity_level=verbosity_level,
            planning_interval=self.planning_interval,
            stream_outputs=True,
            **kwargs,
        )
        self.prompt_templates["system_prompt"] = SELENIUM_SYSTEM_PROMPT_TEMPLATE.replace(
            "<<resolution_x>>", str(self.width)
        ).replace("<<resolution_y>>", str(self.height))

        # Add screen info to state
        self.state["screen_width"] = self.width
        self.state["screen_height"] = self.height

        # Add default tools
        self.logger.log("Setting up agent tools...")
        self._setup_desktop_tools()
        self._setup_step_callbacks([self.take_screenshot_callback])

        
    def _setup_network_monitoring(self):
        """Setup Chrome DevTools Protocol for network monitoring"""
        # Enable network domain
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        # Clear any existing network requests
        self.network_requests = []
        
        # Add event listeners for network requests
        self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        
        # Set up event listener callback (note: this is a simplified approach)
        # In practice, you'd need to use CDP event streaming for real-time capture
        print("Network monitoring enabled")

    
    def capture_current_network_activity(self) -> list[dict[str, Any]]:
        """Capture current network activity using CDP"""
        # Get performance logs which include network requests
        logs = self.driver.get_log('performance')
        
        current_requests = []
        for log in logs:
            message = json.loads(log['message'])
            if message.get('message', {}).get('method') == 'Network.requestWillBeSent':
                params = message.get('message', {}).get('params', {})
                request_info = {
                    'timestamp': log['timestamp'] / 1000,  # Convert to seconds
                    'url': params.get('request', {}).get('url', ''),
                    'method': params.get('request', {}).get('method', 'GET'),
                    'headers': params.get('request', {}).get('headers', {}),
                    'post_data': params.get('request', {}).get('postData', ''),
                    'request_id': params.get('requestId', '')
                }
                current_requests.append(request_info)
                
        return current_requests
    
    def _capture_network_request(self, request_data: dict[str, Any]) -> None:
        """Capture and store network request data"""
        # Extract relevant information from the request
        request_info = {
            'timestamp': time.time(),
            'url': request_data.get('url', ''),
            'method': request_data.get('method', 'GET'),
            'headers': request_data.get('headers', {}),
            'post_data': request_data.get('postData', ''),
            'request_id': request_data.get('requestId', '')
        }
        self.network_requests.append(request_info)
    
    def get_network_requests_since_last_clear(self) -> list[dict[str, Any]]:
        """Get all network requests since the last clear and return formatted data"""
        return self.network_requests.copy()
    
    def clear_network_requests(self) -> None:
        """Clear the network requests buffer"""
        self.network_requests = []
        print("Network requests buffer cleared")
    
    def get_network_requests_as_har_like(self) -> dict[str, Any]:
        """Format network requests in a HAR-like structure"""
        har_like = {
            'version': '1.0',
            'creator': {
                'name': 'SeleniumVisionAgent',
                'version': '1.0'
            },
            'entries': []
        }
        
        for req in self.network_requests:
            entry = {
                'startedDateTime': datetime.fromtimestamp(req['timestamp']).isoformat(),
                'request': {
                    'method': req['method'],
                    'url': req['url'],
                    'headers': [{'name': k, 'value': v} for k, v in req['headers'].items()],
                    'postData': req['post_data'] if req['post_data'] else None
                },
                'response': {},  # Response data would need additional CDP events
                'cache': {},
                'timings': {}
            }
            har_like['entries'].append(entry)
        
        return har_like
        
    def save_screenshot(self, memory_step: ActionStep, agent: CodeAgent) -> None:
        time.sleep(1.0)  # Let JavaScript animations happen before taking the screenshot
        
        current_step = memory_step.step_number
        if self.driver is not None:
            for previous_memory_step in agent.memory.steps:  # Remove previous screenshots for lean processing
                if isinstance(previous_memory_step, ActionStep) and previous_memory_step.step_number <= current_step - 2:
                    previous_memory_step.observations_images = None
            png_bytes = self.driver.get_screenshot_as_png()
            image = Image.open(BytesIO(png_bytes))
            print(f"Captured a browser screenshot: {image.size} pixels")
            memory_step.observations_images = [image.copy()]  # Create a copy to ensure it persists

        # Update observations with current URL
        url_info = f"Current url: {self.driver.current_url}"
        memory_step.observations = (
            url_info if memory_step.observations is None else memory_step.observations + "\n" + url_info
        )

    def _setup_desktop_tools(self):
        """Register all desktop tools"""

        @tool
        def click(x: int, y: int) -> str:
            """
            Performs a left-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x, y).click().perform()
            action.reset_actions()
            self.click_coordinates = [x, y]
            self.logger.log(f"Clicked at coordinates ({x}, {y})")
            return f"Clicked at coordinates ({x}, {y})"

        @tool
        def right_click(x: int, y: int) -> str:
            """
            Performs a right-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x, y).context_click().perform()
            action.reset_actions()
            self.click_coordinates = [x, y]
            self.logger.log(f"Right-clicked at coordinates ({x}, {y})")
            return f"Right-clicked at coordinates ({x}, {y})"

        @tool
        def double_click(x: int, y: int) -> str:
            """
            Performs a double-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x, y).double_click().perform()
            action.reset_actions()
            self.click_coordinates = [x, y]
            self.logger.log(f"Double-clicked at coordinates ({x}, {y})")
            return f"Double-clicked at coordinates ({x}, {y})"

        @tool
        def move_mouse(x: int, y: int) -> str:
            """
            Moves the mouse cursor to the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x, y).perform()
            action.reset_actions()
            self.logger.log(f"Moved mouse to coordinates ({x}, {y})")
            return f"Moved mouse to coordinates ({x}, {y})"

        def normalize_text(text):
            return "".join(
                c
                for c in unicodedata.normalize("NFD", text)
                if not unicodedata.combining(c)
            )

        @tool
        def type_text(text: str) -> str:
            """
            Types the specified text at the current cursor position.
            Args:
                text: The text to type
            """
            clean_text = normalize_text(text)
            action = ActionChains(self.driver)
            action.send_keys(clean_text).perform()
            action.reset_actions()
            self.logger.log(f"Typed text: '{clean_text}'")
            return f"Typed text: '{clean_text}'"

        @tool
        def press_key(key: str) -> str:
            """
            Presses a keyboard key
            Args:
                key: The key to press (e.g. "enter", "space", "backspace", etc.).
            """
            # Map common key names to Selenium Keys
            key_mapping = {
                'enter': Keys.ENTER,
                'space': Keys.SPACE,
                'backspace': Keys.BACKSPACE,
                'tab': Keys.TAB,
                'escape': Keys.ESCAPE,
                'esc': Keys.ESCAPE,
                'delete': Keys.DELETE,
                'shift': Keys.SHIFT,
                'ctrl': Keys.CONTROL,
                'alt': Keys.ALT
            }
            selenium_key = key_mapping.get(key.lower(), key)
            action = ActionChains(self.driver)
            action.send_keys(selenium_key).perform()
            action.reset_actions()
            self.logger.log(f"Pressed key: {key}")
            return f"Pressed key: {key}"

        @tool
        def go_back() -> str:
            """
            Goes back to the previous page in the browser. If using this tool doesn't work, just click the button directly.
            Args:
            """
            self.driver.back()
            self.logger.log("Went back one page")
            return "Went back one page"

        @tool
        def drag_and_drop(x1: int, y1: int, x2: int, y2: int) -> str:
            """
            Clicks [x1, y1], drags mouse to [x2, y2], then release click.
            Args:
                x1: origin x coordinate
                y1: origin y coordinate
                x2: end x coordinate
                y2: end y coordinate
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x1, y1).click_and_hold().move_by_offset(x2-x1, y2-y1).release().perform()
            action.reset_actions()
            message = f"Dragged and dropped from [{x1}, {y1}] to [{x2}, {y2}]"
            self.logger.log(message)
            return message

        @tool
        def scroll(x: int, y: int, direction: str = "down", amount: int = 2) -> str:
            """
            Moves the mouse to selected coordinates, then scrolls the page.
            Args:
                x: The x coordinate (horizontal position) of the element to scroll
                y: The y coordinate (vertical position) of the element to scroll
                direction: The direction to scroll ("up" or "down"), defaults to "down".
                amount: The amount to scroll. A good amount is 1 or 2.
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x, y)
            for _ in range(amount):
                if direction.lower() == "up":
                    action.scroll_by_amount(0, -100)
                else:
                    action.scroll_by_amount(0, 100)
            action.perform()
            action.reset_actions()
            message = f"Scrolled {direction} by {amount}"
            self.logger.log(message)
            return message

        @tool
        def wait(seconds: float) -> str:
            """
            Waits for the specified number of seconds. Very useful in case the prior order is still executing (for example starting very heavy applications like browsers or office apps)
            Args:
                seconds: Number of seconds to wait, generally 3 is enough.
            """
            time.sleep(seconds)
            self.logger.log(f"Waited for {seconds} seconds")
            return f"Waited for {seconds} seconds"

        @tool
        def open_url(url: str) -> str:
            """
            Directly opens the specified URL in the browser.
            Args:
                url: The URL to open
            """
            # Make sure URL has http/https prefix
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            self.driver.get(url)
            # Give it time to load
            time.sleep(2)
            self.logger.log(f"Opening URL: {url}")
            return f"Opened URL: {url}"

        @tool
        def find_on_page_ctrl_f(search_string: str) -> str:
            """
            Scroll the browser viewport to the first occurrence of the search string. This is equivalent to Ctrl+F.
            Args:
                search_string: The string to search for on the page.
            """
            action = ActionChains(self.driver)
            action.key_down(Keys.CONTROL).send_keys('f').key_up(Keys.CONTROL).perform()
            time.sleep(0.3)
            clean_text = normalize_text(search_string)
            action.send_keys(clean_text).perform()
            time.sleep(0.3)
            action.send_keys(Keys.ENTER).perform()
            time.sleep(0.3)
            action.send_keys(Keys.ESCAPE).perform()
            action.reset_actions()
            output_message = f"Scrolled to the first occurrence of '{clean_text}'"
            self.logger.log(output_message)
            return output_message

        @tool
        def get_network_requests() -> str:
            """
            Retrieves all network requests made since the last interaction or since monitoring started.
            This provides information similar to HAR (HTTP Archive) files.
            Returns a summary of network requests with URLs, methods, and timestamps.
            """
            # Capture current network activity from performance logs
            current_activity = self.capture_current_network_activity()
            
            # Combine with any previously stored requests
            all_requests = self.network_requests + current_activity
            
            if not all_requests:
                return "No network requests captured since last interaction."
            
            # Format the output for the agent
            summary = f"Captured {len(all_requests)} network requests:\n"
            for i, req in enumerate(all_requests, 1):
                timestamp_str = datetime.fromtimestamp(req['timestamp']).strftime('%H:%M:%S.%f')[:-3]
                summary += f"{i}. [{timestamp_str}] {req['method']} {req['url']}\n"
                if req['post_data']:
                    summary += f"   POST data: {req['post_data'][:100]}{'...' if len(req['post_data']) > 100 else ''}\n"
            
            # Store the requests for potential future use
            self.network_requests.extend(current_activity)
            
            return summary

        @tool
        def clear_network_requests_buffer() -> str:
            """
            Clears the buffer of captured network requests.
            Useful to start fresh monitoring from a specific point.
            """
            self.clear_network_requests()
            return "Network requests buffer cleared. Starting fresh network monitoring."
        
        @tool
        def get_network_requests_json() -> str:
            """
            Get detailed network requests in JSON format (HAR-like structure).
            Returns comprehensive information about all captured network requests.
            """
            # Capture current network activity
            current_activity = self.capture_current_network_activity()
            all_requests = self.network_requests + current_activity
            
            if not all_requests:
                return "No network requests to export."
            
            # Get HAR-like structure
            har_data = self.get_network_requests_as_har_like()
            
            # Update with current requests
            har_data['entries'] = []
            for req in all_requests:
                entry = {
                    'startedDateTime': datetime.fromtimestamp(req['timestamp']).isoformat(),
                    'request': {
                        'method': req['method'],
                        'url': req['url'],
                        'headers': [{'name': k, 'value': v} for k, v in req['headers'].items()],
                        'postData': {'text': req['post_data']} if req['post_data'] else None
                    }
                }
                har_data['entries'].append(entry)
            
            return json.dumps(har_data, indent=2)

        # Register the tools
        self.tools["click"] = click
        self.tools["right_click"] = right_click
        self.tools["double_click"] = double_click
        self.tools["move_mouse"] = move_mouse
        self.tools["type_text"] = type_text
        self.tools["press_key"] = press_key
        self.tools["scroll"] = scroll
        self.tools["wait"] = wait
        self.tools["open_url"] = open_url
        self.tools["go_back"] = go_back
        self.tools["drag_and_drop"] = drag_and_drop
        self.tools["find_on_page_ctrl_f"] = find_on_page_ctrl_f
        self.tools["get_network_requests"] = get_network_requests
        # self.tools["clear_network_requests_buffer"] = clear_network_requests_buffer
        # self.tools["get_network_requests_json"] = get_network_requests_json

    def take_screenshot_callback(self, memory_step: ActionStep, agent=None) -> None:
        """Callback that takes a screenshot + memory snapshot after a step completes"""
        self.logger.log("Analyzing screen content...")

        current_step = memory_step.step_number

        time.sleep(2.5)  # Let things happen in the browser
        screenshot_bytes = self.driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot_bytes))

        # Create a filename with step number
        screenshot_path = os.path.join(self.data_dir, f"step_{current_step:03d}.png")
        image.save(screenshot_path)

        image_copy = image.copy()

        if getattr(self, "click_coordinates", None):
            print("DRAWING MARKER")
            image_copy = draw_marker_on_image(image_copy, self.click_coordinates)

        self.last_marked_screenshot = AgentImage(screenshot_path)
        print(f"Saved screenshot for step {current_step} to {screenshot_path}")

        for previous_memory_step in (
            agent.memory.steps
        ):  # Remove previous screenshots from logs for lean processing
            if (
                isinstance(previous_memory_step, ActionStep)
                and previous_memory_step.step_number <= current_step - 1
            ):
                previous_memory_step.observations_images = None
            elif isinstance(previous_memory_step, TaskStep):
                previous_memory_step.task_images = None

            if (
                isinstance(previous_memory_step, ActionStep)
                and previous_memory_step.step_number == current_step - 1
            ):
                if (
                    previous_memory_step.tool_calls
                    and getattr(previous_memory_step.tool_calls[0], "arguments", None)
                    and memory_step.tool_calls
                    and getattr(memory_step.tool_calls[0], "arguments", None)
                ):
                    if (
                        previous_memory_step.tool_calls[0].arguments
                        == memory_step.tool_calls[0].arguments
                    ):
                        memory_step.observations += "\nWARNING: You've executed the same action several times in a row. MAKE SURE TO NOT UNNECESSARILY REPEAT ACTIONS."

        # Add the marker-edited image to the current memory step
        memory_step.observations_images = [image_copy]

        # memory_step.observations_images = [screenshot_path] # IF YOU USE THIS INSTEAD OF ABOVE, LAUNCHING A SECOND TASK BREAKS

        self.click_coordinates = None  # Reset click marker

    def close(self):
        """Clean up resources"""
        if self.driver:
            print("Closing browser...")
            self.driver.quit()
            print("Browser closed")

if __name__ == "__main__":
    
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
    )
    selenium_vision_agent = SeleniumVisionAgent(model=model, data_dir="data")
    selenium_vision_agent.run("""
I want you to go to github.com, to look for the numpy package and click the button to see all of the labels. 
              
When you are done, I want you to give me a list of the requests that were made to the server. 
              
              """)

    selenium_vision_agent.tools["open_url"]("https://github.com/numpy/numpy/issues")
    selenium_vision_agent.tools["get_network_requests"]()
    pass
    
    