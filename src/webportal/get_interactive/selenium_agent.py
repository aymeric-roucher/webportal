import os
import time
import unicodedata
import json
import requests
from datetime import datetime
from io import BytesIO
from typing import Any
from urllib.parse import urljoin, urlparse

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
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        self.driver = webdriver.Chrome(options=chrome_options)

        # Initialize network request tracking
        self.network_requests = []
        self.step_requests = {}  # step_number -> list of requests for that step
        self.last_processed_log_count = 0  # Track processed logs to get only new ones
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
        self.prompt_templates["system_prompt"] = (
            SELENIUM_SYSTEM_PROMPT_TEMPLATE.replace(
                "<<resolution_x>>", str(self.width)
            ).replace("<<resolution_y>>", str(self.height))
        )

        # Add screen info to state
        self.state["screen_width"] = self.width
        self.state["screen_height"] = self.height

        # Add default tools
        self.logger.log("Setting up agent tools...")
        self._setup_desktop_tools()
        self._setup_step_callbacks([self.take_screenshot_callback, self.capture_requests_callback])

    def _setup_network_monitoring(self):
        """Setup Chrome DevTools Protocol for network monitoring"""
        # Enable network domain
        self.driver.execute_cdp_cmd("Network.enable", {})

        # Clear any existing network requests
        self.network_requests = []

        # Add event listeners for network requests
        self.driver.execute_cdp_cmd("Network.clearBrowserCache", {})

        # Set up event listener callback (note: this is a simplified approach)
        # In practice, you'd need to use CDP event streaming for real-time capture
        print("Network monitoring enabled")

    def capture_step_network_activity(self, step_number: int) -> list[dict[str, Any]]:
        """Capture network activity that happened during a specific step"""
        # Get all current logs
        logs = self.driver.get_log("performance")

        # Only process new logs since last capture
        new_logs = logs[self.last_processed_log_count :]
        self.last_processed_log_count = len(logs)

        if not new_logs:
            return []

        # Temporary storage for this step's requests and responses
        requests_map = {}
        responses_map = {}

        # Process new logs only
        for log in new_logs:
            message = json.loads(log["message"])
            method = message.get("message", {}).get("method")
            params = message.get("message", {}).get("params", {})

            if method == "Network.requestWillBeSent":
                request_id = params.get("requestId", "")
                if request_id:
                    requests_map[request_id] = {
                        "timestamp": log["timestamp"] / 1000,
                        "url": params.get("request", {}).get("url", ""),
                        "method": params.get("request", {}).get("method", "GET"),
                        "headers": params.get("request", {}).get("headers", {}),
                        "post_data": params.get("request", {}).get("postData", ""),
                        "request_id": request_id,
                        "step_number": step_number,
                        "type": params.get("type", ""),
                    }

            elif method == "Network.responseReceived":
                request_id = params.get("requestId", "")
                if (
                    request_id and request_id in requests_map
                ):  # Only for requests we captured in this step
                    response_info = params.get("response", {})
                    response_data = {
                        "status_code": response_info.get("status", 0),
                        "status_text": response_info.get("statusText", ""),
                        "headers": response_info.get("headers", {}),
                        "mime_type": response_info.get("mimeType", ""),
                        "url": response_info.get("url", ""),
                        "response_timestamp": log["timestamp"] / 1000,
                    }
                    
                    # Try to get the response body
                    try:
                        body_result = self.driver.execute_cdp_cmd(
                            "Network.getResponseBody", {"requestId": request_id}
                        )
                        response_data["body"] = body_result.get("body")
                        response_data["base64Encoded"] = body_result.get("base64Encoded", False)
                    except Exception as e:
                        response_data["body"] = None
                        response_data["body_error"] = str(e)
                    
                    responses_map[request_id] = response_data

        # Combine requests with responses for this step
        step_requests = []
        for request_id, request_info in requests_map.items():
            if request_id in responses_map:
                request_info["response"] = responses_map[request_id]
            else:
                request_info["response"] = None
            step_requests.append(request_info)

        # Store step requests for later analysis
        self.step_requests[step_number] = step_requests

        return step_requests

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
                "enter": Keys.ENTER,
                "space": Keys.SPACE,
                "backspace": Keys.BACKSPACE,
                "tab": Keys.TAB,
                "escape": Keys.ESCAPE,
                "esc": Keys.ESCAPE,
                "delete": Keys.DELETE,
                "shift": Keys.SHIFT,
                "ctrl": Keys.CONTROL,
                "alt": Keys.ALT,
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
            action.move_by_offset(x1, y1).click_and_hold().move_by_offset(
                x2 - x1, y2 - y1
            ).release().perform()
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
            action.key_down(Keys.CONTROL).send_keys("f").key_up(Keys.CONTROL).perform()
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
        
    def capture_requests_callback(self, memory_step: ActionStep| None = None, agent: CodeAgent | None =None) -> None:
        """Callback that captures the requests for a step"""
        # Capture network requests for this specific step
        current_step = memory_step.step_number if memory_step else 0
        self.logger.log(f"Capturing network requests for step {current_step}")
        
        step_requests = self.capture_step_network_activity(current_step)
        if step_requests:
            self.logger.log(
                f"Captured {len(step_requests)} network requests for step {current_step}"
            )
            # Analyze the requests for this step
            self._analyze_step_requests(current_step, step_requests, memory_step)
            
    def take_screenshot_callback(self, memory_step: ActionStep, agent: CodeAgent | None =None) -> None:
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

    def _filter_relevant_requests(
        self, requests_list: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Filter requests to keep only relevant API calls (fetch/XHR, not static assets)"""
        relevant_requests = []

        # Extensions to exclude (static assets)
        static_extensions = {
            ".js",
            ".css",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".svg",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".mp4",
            ".mp3",
            ".pdf",
        }

        for request in requests_list:
            # Skip None requests
            if request is None:
                continue
                
            url = request.get("url", "")
            method = request.get("method", "GET")
            request_type = request.get("type", "")

            # Skip empty URLs
            if not url:
                continue

            # Parse URL to check extension
            parsed_url = urlparse(url)
            path = parsed_url.path.lower()

            # Skip static assets
            if any(path.endswith(ext) for ext in static_extensions):
                continue

            # Skip non-HTTP URLs
            if not url.startswith(("http://", "https://")):
                continue

            # Keep XHR/Fetch requests, API-like URLs, or Document requests (initial page loads)
            if (
                request_type in ["XHR", "Fetch", "Document"]  # Include Document type for initial page loads
                or "/api/" in url
                or "/graphql" in url
                or "/ajax" in url
                or method in ["POST", "PUT", "PATCH", "DELETE"]
                or "application/json" in str(request.get("headers", {}))
            ):
                relevant_requests.append(request)

        relevant_requests_filtered_by_type_and_body = []
        for request in relevant_requests:
            # Skip None requests
            if request is None:
                continue
            if request.get("type") in ["XHR", "Fetch", "Document"]:
                if request.get("response") is not None:
                    if request.get("response").get("body"):
                        relevant_requests_filtered_by_type_and_body.append(request)
            else:
                continue
            
        relevant_requests_filtered_by_json_body = []
        for request in relevant_requests_filtered_by_type_and_body:
            # Skip None requests
            if request is None:
                continue
            if request.get("response", {}).get("body"):
                try:
                    json.loads(request.get("response", {}).get("body"))
                    relevant_requests_filtered_by_json_body.append(request)
                except json.JSONDecodeError:
                    continue
                
        relevant_requests_filtered_by_html_body = []
        for request in relevant_requests_filtered_by_type_and_body:
            # Skip None requests
            if request is None:
                continue
            if request.get("response", {}).get("body"):
                body = request.get("response", {}).get("body")
                if body and "DOCTYPE" in body:
                    relevant_requests_filtered_by_html_body.append(request)
                else:
                    continue
        return relevant_requests_filtered_by_json_body, relevant_requests_filtered_by_html_body

    def _test_request_independently(self, request: dict[str, Any]) -> dict[str, Any]:
        """Test a request independently to see if it works without browser context"""

        # If we already have response data from browser capture, use it as reference
        original_response = request.get("response")
        if original_response:
            original_status = original_response.get("status_code")
            print(
                f"Original browser response: {original_status} {original_response.get('status_text', '')}"
            )

        # Get current cookies from the browser to maintain session
        browser_cookies = self.driver.get_cookies()
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in browser_cookies}

        # Base headers similar to agent.py
        base_headers = {
            "sec-fetch-site": "same-origin",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "referer": self.driver.current_url,
        }

        # Merge with original request headers
        original_headers = request.get("headers", {})
        headers = {**base_headers, **original_headers}

        try:
            url = request["url"]
            method = request.get("method", "GET").upper()

            if method == "GET":
                response = requests.get(
                    url, headers=headers, cookies=cookies_dict, timeout=10
                )
            elif method == "POST":
                post_data = request.get("post_data", "")
                if post_data:
                    # Try to parse as JSON first
                    try:
                        json_data = json.loads(post_data)
                        response = requests.post(
                            url,
                            headers=headers,
                            cookies=cookies_dict,
                            json=json_data,
                            timeout=10,
                        )
                    except json.JSONDecodeError:
                        # Send as raw data if not JSON
                        response = requests.post(
                            url,
                            headers=headers,
                            cookies=cookies_dict,
                            data=post_data,
                            timeout=10,
                        )
                else:
                    response = requests.post(
                        url, headers=headers, cookies=cookies_dict, timeout=10
                    )
            else:
                # For other methods (PUT, PATCH, DELETE)
                response = requests.request(
                    method, url, headers=headers, cookies=cookies_dict, timeout=10
                )

            # Check if request was successful
            response.raise_for_status()

            # Try to parse response
            try:
                response_data = response.json()
                # Check for GraphQL-style errors
                if isinstance(response_data, dict) and "errors" in response_data:
                    return {
                        "success": False,
                        "error": f"API returned errors: {response_data['errors']}",
                        "status_code": response.status_code,
                    }
                return {
                    "success": True,
                    "response_data": response_data,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", "unknown"),
                    "original_response": original_response,
                }
            except json.JSONDecodeError:
                # Not JSON, might be HTML or plain text
                return {
                    "success": True,
                    "response_data": response.text[:1000]
                    + ("..." if len(response.text) > 1000 else ""),
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", "unknown"),
                    "original_response": original_response,
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out (likely requires user interaction or session)",
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection error (possibly CORS or network restriction)",
            }
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            if status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication required (401 Unauthorized)",
                }
            elif status_code == 403:
                return {
                    "success": False,
                    "error": "Access forbidden (403) - likely anti-bot protection or insufficient permissions",
                }
            elif status_code == 429:
                return {
                    "success": False,
                    "error": "Rate limited (429) - too many requests",
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP error {status_code}: {str(e)}",
                }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def _generate_markdown_explanation(
        self, request: dict[str, Any], result: dict[str, Any]
    ) -> str:
        """Generate a markdown explanation for a successful request"""
        url = request["url"]
        method = request.get("method", "GET")
        headers = request.get("headers", {})
        post_data = request.get("post_data", "")

        # Parse URL components
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        endpoint = parsed_url.path
        query_params = parsed_url.query

        # Get original response info if available
        original_response = result.get("original_response")
        original_status = (
            original_response.get("status_code") if original_response else None
        )

        markdown = f"""## {method} {endpoint}

**Base URL**: `{base_url}`
**Full URL**: `{url}`

### Description
This endpoint appears to handle {"data submission" if method in ["POST", "PUT", "PATCH"] else "data retrieval"}{"with query parameters" if query_params else ""}.

### Request Details
- **Method**: {method}
- **Content-Type**: {result.get("content_type", "unknown")}
- **Status Code**: {result.get("status_code", "unknown")}"""

        if original_status and original_status != result.get("status_code"):
            markdown += f"""
- **Original Browser Status**: {original_status} (may differ from independent test)"""

        markdown += "\n\n"

        # Add headers if significant ones exist
        important_headers = {
            k: v
            for k, v in headers.items()
            if k.lower() in ["authorization", "content-type", "x-api-key", "accept"]
        }
        if important_headers:
            markdown += "### Important Headers\n"
            for header, value in important_headers.items():
                # Mask sensitive values
                display_value = (
                    value if "authorization" not in header.lower() else "[MASKED]"
                )
                markdown += f"- `{header}`: `{display_value}`\n"
            markdown += "\n"

        # Add query parameters if they exist
        if query_params:
            markdown += f"### Query Parameters\n`{query_params}`\n\n"

        # Add POST data if it exists
        if post_data and method in ["POST", "PUT", "PATCH"]:
            markdown += "### Request Body\n"
            try:
                # Try to pretty-print JSON
                json_data = json.loads(post_data)
                markdown += f"```json\n{json.dumps(json_data, indent=2)}\n```\n\n"
            except json.JSONDecodeError:
                markdown += f"```\n{post_data}\n```\n\n"

        # Add response sample
        response_data = result.get("response_data")
        if response_data:
            markdown += "### Response Sample\n"
            if isinstance(response_data, dict):
                markdown += f"```json\n{json.dumps(response_data, indent=2)}\n```\n\n"
            else:
                # Truncate long text responses
                sample = str(response_data)[:500] + (
                    "..." if len(str(response_data)) > 500 else ""
                )
                markdown += f"```\n{sample}\n```\n\n"

        # Add usage example
        markdown += f"""### Example Usage

```python
import requests

response = requests.{method.lower()}(
    "{url}"{"," if method in ["POST", "PUT", "PATCH"] and post_data else ""}
"""

        if method in ["POST", "PUT", "PATCH"] and post_data:
            try:
                json.loads(post_data)
                markdown += f"    json={post_data}"
            except json.JSONDecodeError:
                markdown += f'    data="""{post_data}"""'

        markdown += f"""
)

if response.status_code == 200:
    data = response.json()  # or response.text for non-JSON
    # Process the data...
```

"""

        return markdown

    def _generate_failure_explanation(
        self, request: dict[str, Any], result: dict[str, Any]
    ) -> str:
        """Generate an explanation for why a request failed"""
        url = request["url"]
        method = request.get("method", "GET")
        error = result.get("error", "Unknown error")

        explanation = f"""❌ **{method} {url}**

**Failure Reason**: {error}

**Likely Causes**:
"""

        if "Authentication required" in error or "401" in error:
            explanation += "- This endpoint requires user authentication\n- The API likely needs login tokens, API keys, or session cookies\n- Access is restricted to authenticated users only\n"
        elif "Access forbidden" in error or "403" in error:
            explanation += "- Anti-bot protection is active (Cloudflare, bot detection, etc.)\n- The endpoint requires specific permissions or roles\n- Request might be missing required headers or tokens\n"
        elif "Rate limited" in error or "429" in error:
            explanation += "- Too many requests were made in a short time\n- The API has rate limiting enabled\n- Would need to implement proper request throttling\n"
        elif "CORS" in error or "Connection error" in error:
            explanation += "- Cross-Origin Resource Sharing (CORS) restrictions\n- The API doesn't allow requests from external origins\n- Would only work from the original website's domain\n"
        elif "timed out" in error:
            explanation += "- The request requires user interaction or real-time session data\n- The endpoint might be slow or temporarily unavailable\n- Could require specific timing or sequential requests\n"
        else:
            explanation += "- The endpoint might require specific request parameters\n- Could need additional headers or authentication\n- Might be a temporary server issue\n"

        explanation += f"""
**What this endpoint likely does**:
Based on the URL pattern `{url}`, this appears to be {"an API endpoint for data modification" if method in ["POST", "PUT", "PATCH", "DELETE"] else "a data retrieval endpoint"}.

**Recommendation**: This endpoint cannot be used independently and would require the full browser context, session, and potentially user interaction to work properly.
"""

        return explanation

    def _analyze_step_requests(
        self, step_number: int, requests: list[dict[str, Any]], memory_step: ActionStep | None = None
    ):
        """Analyze requests from a specific step and generate markdown summaries"""

        # Filter requests to get JSON and HTML responses separately
        json_requests, html_requests = self._filter_relevant_requests(requests)
        
        if not json_requests and not html_requests:
            return

        print(f"\n=== STEP {step_number} REQUEST ANALYSIS ===")
        print(f"Found {len(json_requests)} JSON requests and {len(html_requests)} HTML requests")

        # Get the action that was performed in this step
        action_description = self._get_step_action_description(memory_step)
        tool_call_info = self._get_tool_call_info(memory_step)
        
        # Generate markdown for this step
        markdown_summary = self._generate_step_markdown(
            step_number, action_description, tool_call_info, json_requests, html_requests
        )
        
        if markdown_summary:
            self._save_step_markdown(step_number, markdown_summary)

    def _get_step_action_description(self, memory_step: ActionStep | None = None) -> str:
        """Extract a description of what action was performed in this step"""
        if memory_step and memory_step.tool_calls:
            tool_call = memory_step.tool_calls[0]
            tool_name = tool_call.name
            args = getattr(tool_call, "arguments", {})

            if tool_name == "click":
                return f"clicked at coordinates ({args.get('x', '?')}, {args.get('y', '?')})"
            elif tool_name == "type_text":
                return f"typed text: '{args.get('text', '?')}'"
            elif tool_name == "open_url":
                return f"opened URL: {args.get('url', '?')}"
            elif tool_name == "scroll":
                direction = args.get("direction", "down")
                return f"scrolled {direction}"
            elif tool_name == "press_key":
                return f"pressed key: {args.get('key', '?')}"
            else:
                return f"performed {tool_name} action"

        return "performed unknown action"
    
    def _get_tool_call_info(self, memory_step: ActionStep | None = None) -> dict[str, Any]:
        """Extract tool call information for markdown generation"""
        if memory_step and memory_step.tool_calls:
            tool_call = memory_step.tool_calls[0]
            return {
                "tool_name": tool_call.name,
                "arguments": getattr(tool_call, "arguments", {})
            }
        return {"tool_name": "unknown", "arguments": {}}
    
    def _generate_step_markdown(
        self, 
        step_number: int, 
        action_description: str, 
        tool_call_info: dict[str, Any],
        json_requests: list[dict[str, Any]], 
        html_requests: list[dict[str, Any]]
    ) -> str:
        """Generate markdown summary for a step in the interactive_element format"""
        
        if not json_requests and not html_requests:
            return ""
        
        # Try to infer element type from action
        element_type = self._infer_element_type(tool_call_info, action_description)
        
        # Get current page location (simplified)
        current_url = self.driver.current_url if hasattr(self, 'driver') else "unknown"
        location_page = self._extract_location_page(current_url)
        
        markdown = f"""```interactive_element_step_{step_number}
location_page: {location_page}
type: {element_type}
visual_element: {action_description}
trigger: {tool_call_info['tool_name']} with args {tool_call_info['arguments']}
"""
        
        # Generate separate markdown sections for JSON and HTML requests
        if json_requests:
            markdown += self._generate_json_requests_section(json_requests, action_description)
        
        if html_requests:
            markdown += self._generate_html_requests_section(html_requests, action_description)
        
        # Add viewport effect
        viewport_effect = self._describe_viewport_effect(action_description)
        markdown += f"viewport_effect: {viewport_effect}\n"
        
        markdown += "```\n"
        return markdown
    
    def _generate_json_requests_section(self, json_requests: list[dict[str, Any]], action_description: str) -> str:
        """Generate markdown section for JSON API requests"""
        section = ""
        
        for i, request in enumerate(json_requests):
            url = request.get('url', '')
            method = request.get('method', 'GET')
            
            if i == 0:  # Primary request
                section += f"request: {method} {url}\n"
                
                # Add request arguments if it's a POST with data
                post_data = request.get('post_data', '')
                if post_data and method in ['POST', 'PUT', 'PATCH']:
                    section += f"arguments:\n"
                    try:
                        json_data = json.loads(post_data)
                        # Truncate large JSON for readability
                        json_str = json.dumps(json_data)
                        if len(json_str) > 500:
                            json_str = json_str[:500] + "..."
                        section += f'  "body" (json): {json_str}\n'
                    except json.JSONDecodeError:
                        post_data_truncated = post_data[:200] + ("..." if len(post_data) > 200 else "")
                        section += f'  "body" (raw): {post_data_truncated}\n'
                
                # Add effect description
                effect = self._describe_request_effect(request, action_description)
                section += f"effect: {effect}\n"
            
            # Add response details for all JSON requests
            response_data = request.get('response', {})
            response_body = response_data.get('body', '')
            
            if response_body:
                try:
                    json_response = json.loads(response_body)
                    
                    if i == 0:  # Primary request gets detailed response info
                        section += f"returns: JSON API response\n"
                        section += f"response_structure:\n"
                        
                        if isinstance(json_response, dict):
                            keys = list(json_response.keys())[:10]  # More keys for LLM
                            section += f"  keys: {keys}\n"
                            
                            # Extract important data patterns for LLM
                            if 'data' in json_response:
                                data_info = self._describe_data_field(json_response['data'])
                                section += f"  data: {data_info}\n"
                            
                            if 'errors' in json_response:
                                section += f"  has_errors: true\n"
                            
                            # Look for pagination info
                            if any(key in json_response for key in ['pageInfo', 'pagination', 'hasNextPage']):
                                section += f"  has_pagination: true\n"
                            
                            # Look for common GraphQL/API patterns
                            if 'nodes' in json_response:
                                nodes_info = self._describe_nodes_field(json_response['nodes'])
                                section += f"  nodes: {nodes_info}\n"
                                
                        elif isinstance(json_response, list):
                            section += f"  type: array\n"
                            section += f"  length: {len(json_response)}\n"
                            if json_response and isinstance(json_response[0], dict):
                                first_keys = list(json_response[0].keys())[:5]
                                section += f"  item_keys: {first_keys}\n"
                    
                    else:  # Additional requests get brief info
                        section += f"additional_request_{i}: {method} {url}\n"
                        if isinstance(json_response, dict):
                            keys = list(json_response.keys())[:5]
                            section += f"  keys: {keys}\n"
                        elif isinstance(json_response, list):
                            section += f"  array_length: {len(json_response)}\n"
                            
                except json.JSONDecodeError:
                    section += f"response_parsing_error: could not parse as JSON\n"
        
        return section
    
    def _generate_html_requests_section(self, html_requests: list[dict[str, Any]], action_description: str) -> str:
        """Generate markdown section for HTML page requests"""
        section = ""
        
        for i, request in enumerate(html_requests):
            url = request.get('url', '')
            method = request.get('method', 'GET')
            
            if i == 0:  # Primary request
                section += f"request: {method} {url}\n"
                
                # Add request arguments if it's a POST with data
                post_data = request.get('post_data', '')
                if post_data and method in ['POST', 'PUT', 'PATCH']:
                    section += f"arguments:\n"
                    section += f'  "body" (form-data): {post_data[:200]}...\n'
                
                # Add effect description
                effect = self._describe_request_effect(request, action_description)
                section += f"effect: {effect}\n"
                section += f"returns: HTML page content\n"
            
            # Add HTML response analysis
            response_data = request.get('response', {})
            response_body = response_data.get('body', '')
            
            if response_body:
                if i == 0:  # Primary request gets detailed HTML info
                    section += f"page_analysis:\n"
                    
                    # Extract page title
                    if "<title>" in response_body:
                        title_start = response_body.find("<title>") + 7
                        title_end = response_body.find("</title>", title_start)
                        if title_end > title_start:
                            title = response_body[title_start:title_end][:100]
                            section += f"  title: {title}\n"
                    
                    # Look for common HTML elements that indicate page type
                    html_indicators = []
                    if 'class="search' in response_body.lower():
                        html_indicators.append('search_page')
                    if 'class="issue' in response_body.lower():
                        html_indicators.append('issues_page')
                    if 'class="repository' in response_body.lower():
                        html_indicators.append('repository_page')
                    if '<form' in response_body.lower():
                        html_indicators.append('has_forms')
                    if 'data-' in response_body.lower():
                        html_indicators.append('has_data_attributes')
                    
                    if html_indicators:
                        section += f"  page_indicators: {html_indicators}\n"
                    
                    # Extract some key content hints for LLM
                    content_preview = response_body[:1000].replace('\n', ' ').replace('\t', ' ')
                    # Clean up multiple spaces
                    import re
                    content_preview = re.sub(r'\s+', ' ', content_preview)
                    section += f"  content_preview: {content_preview}...\n"
                
                else:  # Additional HTML requests
                    section += f"additional_html_request_{i}: {method} {url}\n"
                    if "<title>" in response_body:
                        title_start = response_body.find("<title>") + 7
                        title_end = response_body.find("</title>", title_start)
                        if title_end > title_start:
                            title = response_body[title_start:title_end][:50]
                            section += f"  title: {title}\n"
        
        return section
    
    def _describe_data_field(self, data) -> str:
        """Describe the structure of a 'data' field in JSON response"""
        if isinstance(data, dict):
            keys = list(data.keys())[:5]
            return f"object with keys: {keys}"
        elif isinstance(data, list):
            return f"array with {len(data)} items"
        else:
            return f"value of type {type(data).__name__}"
    
    def _describe_nodes_field(self, nodes) -> str:
        """Describe the structure of a 'nodes' field (common in GraphQL)"""
        if isinstance(nodes, list):
            if nodes and isinstance(nodes[0], dict):
                first_keys = list(nodes[0].keys())[:5]
                return f"array of {len(nodes)} objects with keys: {first_keys}"
            else:
                return f"array with {len(nodes)} items"
        else:
            return f"non-array type: {type(nodes).__name__}"
    
    def _infer_element_type(self, tool_call_info: dict[str, Any], action_description: str) -> str:
        """Infer the UI element type from the action"""
        tool_name = tool_call_info.get('tool_name', '')
        
        if tool_name == 'click':
            if 'button' in action_description.lower():
                return 'Button'
            elif 'dropdown' in action_description.lower() or 'select' in action_description.lower():
                return 'Button/Dropdown'
            elif 'link' in action_description.lower():
                return 'Link'
            else:
                return 'Clickable Element'
        elif tool_name == 'type_text':
            return 'Input Field'
        elif tool_name == 'scroll':
            return 'Scrollable Area'
        else:
            return 'Interactive Element'
    
    def _extract_location_page(self, url: str) -> str:
        """Extract a meaningful location page identifier from URL"""
        if not url or url == 'unknown':
            return 'unknown_page'
        
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        # Handle GitHub-style URLs
        if 'github.com' in parsed.netloc:
            path_parts = path.split('/')
            if len(path_parts) >= 2:
                return f"{path_parts[0]}/{path_parts[1]}/{'/'.join(path_parts[2:])}"
        
        return path if path else parsed.netloc
    
    def _describe_request_effect(self, request: dict[str, Any], action_description: str) -> str:
        """Describe what effect the request has"""
        method = request.get('method', 'GET')
        url = request.get('url', '')
        
        if method == 'GET':
            if 'search' in url.lower():
                return f"Performs search based on {action_description}"
            elif 'sort' in url.lower():
                return f"Sorts content based on {action_description}"
            elif 'filter' in url.lower():
                return f"Filters content based on {action_description}"
            else:
                return f"Retrieves data triggered by {action_description}"
        else:
            return f"Submits data from {action_description}"
    
    
    def _describe_viewport_effect(self, action_description: str) -> str:
        """Describe the visual effect on the viewport"""
        if 'click' in action_description:
            if 'sort' in action_description.lower():
                return "Updates the content display with new sort order"
            elif 'filter' in action_description.lower():
                return "Updates the content display with filtered results"
            elif 'search' in action_description.lower():
                return "Updates the page with search results"
            else:
                return "Updates the page content or navigation"
        elif 'type' in action_description:
            return "Updates input field with typed text"
        elif 'scroll' in action_description:
            return "Changes visible content area"
        else:
            return "Modifies page display or interaction state"
    
    def _save_step_markdown(self, step_number: int, markdown: str):
        """Save the markdown summary for a step"""
        filename = f"step_{step_number:03d}_interactive_element.md"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(markdown)
        
        print(f"💾 Saved interactive element summary to: {filepath}")





