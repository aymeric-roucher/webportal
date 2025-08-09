import os
import time
import unicodedata
from datetime import datetime
from io import BytesIO
from typing import Callable
from pathlib import Path

from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from smolagents import InferenceClientModel, ToolCallingAgent, tool
from smolagents.agent_types import AgentImage
from smolagents.memory import ActionStep, TaskStep
from smolagents.monitoring import LogLevel
from webportal.storage_utils import write_job_file_from_path_to_storage

SELENIUM_SYSTEM_PROMPT_TEMPLATE = """You are a web automation assistant that can control a local browser using Selenium. The current date is <<current_date>>.

You will be given a task to solve in several steps. At each step you will perform an action.
After each action, you'll receive an updated screenshot. 
Then you will proceed as follows, with these sections: don't skip any!

Short term goal: ...
What I see: ...
Outcome of previous action: ...
Reflection: ...
Action:
{"name": "click", "arguments": {"x": 254, "y": 308, "element_description": "button with text 'Submit'"}}
Observation: ...

Akways format your action as JSON blocks as shown above, include the Observation field.

<tools>
You only have access to these tools to interact with the desktop, no additional ones:
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

IMPORTANT: For ALL interaction tools (click, double_click, right_click, type_text, etc.), you MUST provide detailed visual descriptions that include:
- Element type (button, link, input field, dropdown, etc.)
- Visible text content (if any)
- Approximate size (width x height in pixels)
- Visual appearance (color, shape, style)
- Position relative to other elements (e.g., "top-right corner", "below the search bar", "center of the page")
- Any distinguishing visual features

Example good descriptions:
- "rectangular blue button with white text 'Login', approximately 100x35 pixels, located in the top-right corner of the navigation bar"
- "white input field with placeholder text 'Search...', approximately 300x40 pixels, centered at the top of the page with a magnifying glass icon on the right"
- "circular red close button with white 'X', approximately 20x20 pixels, positioned in the top-right corner of the modal dialog"
</click_guidelines>

<task_resolution_example>
For a task like "Go to Google and search for 'Hello World'":
Step 1:
Short term goal: I want to open Google website.
What I see: I see the browser is open but no specific page is loaded yet.
Reflection: I need to navigate to Google first. I'll use the open_url tool to go directly to Google.
Action:
{"name": "open_url", "arguments": {"url": "https://google.com"}}
Observation: ...

Step 2:
Short term goal: I want to search for 'Hello World'.
What I see: I can see the Google homepage with the search box in the center of the page.
Reflection: I can see the Google search box. I need to click on it first and then type my search query.
Action:
{"name": "click", "arguments": {"x": 640, "y": 360, "element_description": "large white rectangular input field with rounded corners, centered on the page with Google logo above it, contains faint gray text 'Search Google or type a URL'"}}
Observation: ...

Step 3:
Short term goal: I want to type 'Hello World' in the search box.
What I see: The search box is now active with a cursor visible.
Reflection: The search box is ready for input. I'll type 'Hello World' now.
Action:
{"name": "type_text", "arguments": {"text": "Hello World", "target_description": "Google search input field with blinking cursor"}}
Observation: ...

Step 4:
Short term goal: I want to submit the search.
What I see: I can see 'Hello World' typed in the search box and there's a search button or I can press Enter.
Reflection: I can either click the search button or press Enter to submit the search. I'll press Enter.
Action:
{"name": "press_key", "arguments": {"key": "enter", "context_description": "to submit the search query in the Google search box"}}
Observation: ...

Step 5:
Short term goal: Verify the search results.
What I see: The Google search results page is showing results for 'Hello World'.
Reflection: Perfect! The search has been completed successfully. I can see search results for 'Hello World' are displayed.
Action:
{"name": "final_answer", "arguments": {"text": "Successfully searched for 'Hello World' on Google"}}
Observation: ...
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
When you've done a click in the previous step, it will be shown by a green crosshair on the screenshot. Use it to check that you didn't click sideways.
In browser, ignore any sign-in popups, cookie banners, or ads while they don't interfere with the elements you want to interact with.
Wait for page elements to load before interacting with them.
</general_guidelines>
""".replace("<<current_date>>", datetime.now().strftime("%A, %d-%B-%Y"))


def draw_marker_on_image(
    image_copy: Image.Image, click_coordinates: list[int]
) -> Image.Image:
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


class SeleniumVisionAgent(ToolCallingAgent):
    """Agent for local browser automation with Selenium and Qwen2.5VL vision capabilities"""

    def __init__(
        self,
        model: InferenceClientModel,
        data_dir: str,
        tools: list[tool] | None = None,
        max_steps: int = 200,
        verbosity_level: LogLevel = 2,
        planning_interval: int | None = None,
        browser_headless: bool = True,
        callback_tools: list[Callable] | None = None,
        job_id: str | None = None,
        domain_name: str | None = None,
        folder_name: str | None = None,
        **kwargs,
    ):
        self.data_dir = data_dir
        self.planning_interval = planning_interval
        self.callback_tools = callback_tools or []
        self.job_id = job_id
        self.domain_name = domain_name
        self.folder_name = folder_name

        self.chrome_options = webdriver.ChromeOptions()
        self.width, self.height = 1280, 720

        if browser_headless:
            # Docker/serverless-friendly Chrome options
            self.chrome_options.add_argument("--headless=new")  # New headless mode
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.add_argument("--disable-gpu")
            self.chrome_options.add_argument("--disable-web-security")
            self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            self.chrome_options.add_argument("--remote-debugging-port=9222")
            self.chrome_options.add_argument("--no-zygote")
            self.chrome_options.add_argument("--disable-default-apps")
            self.chrome_options.add_argument("--disable-extensions")
            self.chrome_options.add_argument("--disable-plugins")

            self.chrome_options.add_argument("--memory-pressure-off")
            self.chrome_options.add_argument("--max_old_space_size=4096")
            self.chrome_options.add_argument("--disable-background-timer-throttling")
            self.chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            self.chrome_options.add_argument("--disable-renderer-backgrounding")
        # Window and display settings
        self.chrome_options.add_argument("--force-device-scale-factor=1")

        self.chrome_options.add_argument(f"--window-size={self.width},{self.height}")
        self.chrome_options.add_argument("--disable-pdf-viewer")
        self.chrome_options.add_argument("--window-position=0,0")

        self._additional_chrome_options()

        self.driver = webdriver.Chrome(options=self.chrome_options)
        
        # Execute stealth JavaScript to mask automation signatures
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                window.chrome = {
                    runtime: {}
                };
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' })
                    })
                });
                delete navigator.__proto__.webdriver;
                window.navigator.chrome = {
                    runtime: {},
                };
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 4,
                });
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
                Object.defineProperty(screen, 'availHeight', {
                    get: () => ''' + str(self.height) + ''',
                });
                Object.defineProperty(screen, 'availWidth', {
                    get: () => ''' + str(self.width) + ''',
                });
            '''
        })

        # Set browser window size
        self.driver.set_window_size(self.width, self.height)
        print(f"Browser window size: {self.width}x{self.height}")

        # Set up temp directory
        os.makedirs(self.data_dir, exist_ok=True)
        print(f"Screenshots and steps will be saved to: {self.data_dir}")

        # Initialize base agent
        super().__init__(
            tools=tools or [],
            model=model,
            max_steps=max_steps,
            verbosity_level=verbosity_level,
            planning_interval=self.planning_interval,
            stream_outputs=True,
            instructions="Don't do parallel tool calls: only one per step.",
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
        self.click_coordinates = None
        self._setup_desktop_tools()
        self.setup_step_callbacks()

    def _additional_chrome_options(self):
        """Advanced stealth options to bypass bot detection"""
        import random
        import os
        
        # Remove automation indicators
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Stealth user agent rotation
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        selected_ua = random.choice(user_agents)
        self.chrome_options.add_argument(f"--user-agent={selected_ua}")
        
        # Language and locale randomization  
        locales = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en-CA,en;q=0.9"]
        self.selected_locale = random.choice(locales)
        
        # Proxy configuration (only if enabled via environment)
        if os.getenv("USE_PROXY", "false").lower() == "true":
            try:
                from webportal.stealth.proxy_manager import get_proxy_manager
                proxy_manager = get_proxy_manager()
                proxy_string = proxy_manager.get_proxy_for_selenium()
                
                if proxy_string:
                    self.chrome_options.add_argument(f"--proxy-server=http://{proxy_string}")
                    print(f"Using proxy: {proxy_string}")
                else:
                    print("No working proxy found, continuing without proxy")
            except Exception as e:
                print(f"Proxy setup failed: {e}")
        
        # Additional stealth arguments
        self.chrome_options.add_argument("--disable-features=VizDisplayCompositor,VizServiceDisplay")
        self.chrome_options.add_argument("--disable-ipc-flooding-protection")
        self.chrome_options.add_argument("--disable-background-networking")
        self.chrome_options.add_argument("--disable-background-mode")
        self.chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        self.chrome_options.add_argument("--disable-client-side-phishing-detection")
        self.chrome_options.add_argument("--disable-domain-reliability")
        self.chrome_options.add_argument("--disable-features=TranslateUI")
        self.chrome_options.add_argument("--disable-sync")
        self.chrome_options.add_argument("--hide-scrollbars")
        self.chrome_options.add_argument("--metrics-recording-only")
        self.chrome_options.add_argument("--mute-audio")
        self.chrome_options.add_argument("--no-default-browser-check")
        self.chrome_options.add_argument("--no-first-run")
        self.chrome_options.add_argument("--disable-logging")
        self.chrome_options.add_argument("--disable-permissions-api")
        self.chrome_options.add_argument("--disable-speech-api")
        self.chrome_options.add_argument("--disable-file-system")
        self.chrome_options.add_argument("--disable-presentation-api")
        self.chrome_options.add_argument("--disable-notifications")
        
        # Randomize window size slightly
        width_offset = random.randint(-50, 50)  
        height_offset = random.randint(-50, 50)
        self.width = max(1280 + width_offset, 1200)
        self.height = max(720 + height_offset, 600)

    def quick_open_url(self, url: str) -> Image.Image:
        self.tools["open_url"](url)
        time.sleep(1.0)
        screenshot_bytes = self.driver.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot_bytes))

    def setup_step_callbacks(self) -> None:
        self._setup_step_callbacks(
            [self.take_screenshot_callback] + self.callback_tools
        )
        
    def _hot_fix_tool_calling_agent_callback(self, memory_step: ActionStep, agent: ToolCallingAgent) -> None:
        """Hot fix for tool calling agent callback, otherwise the output is always misformatted.
        """
        if "with arguments: " in memory_step.model_output:
            memory_step.model_output = memory_step.model_output.split("Tool call ")[0]
        

    def take_screenshot_callback(
        self, memory_step: ActionStep, agent: ToolCallingAgent
    ) -> None:
        """Callback that takes a screenshot + memory snapshot after a step completes"""
        self.logger.log("Analyzing screen content...")

        current_step = memory_step.step_number

        time.sleep(2.5)  # Let things happen in the browser

        screenshot_bytes = self.driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot_bytes))

        # Create a filename with step number
        screenshot_path = os.path.join(self.data_dir, f"step_{current_step:03d}.png")

        image_copy = image.copy()
        if self.click_coordinates:
            print("DRAWING MARKER on coords", self.click_coordinates)
            image_copy = draw_marker_on_image(image_copy, self.click_coordinates)
        image_copy.save(screenshot_path)

        # Save screenshot to job-specific storage if job_id and domain_name are available
        if self.job_id and self.domain_name:
            screenshot_filename = f"step_{current_step:03d}.png"
            if self.folder_name:
                screenshot_filename = f"{self.folder_name}/{screenshot_filename}"
            write_job_file_from_path_to_storage(
                domain_name=self.domain_name, 
                job_id=self.job_id, 
                filename=screenshot_filename, 
                file_path=Path(screenshot_path)
            )

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

        self._hot_fix_tool_calling_agent_callback(memory_step, agent)
        self.click_coordinates = None  # Reset click marker

    def _setup_desktop_tools(self):
        """Register all desktop tools"""

        @tool
        def click(x: int, y: int, element_description: str) -> str:
            """
            Performs a left-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
                element_description: visual description including: element type, text content, size ('big' for instance), color, position relative to other elements (e.g., "blue rectangular button with white text 'Submit', approximately 120x40 pixels, located in the bottom right corner of the form")
            """
            import random
            import time
            
            # Add random human-like delays and movement
            pre_click_delay = random.uniform(0.1, 0.5)
            time.sleep(pre_click_delay)
            
            action = ActionChains(self.driver)
            
            # Add slight randomization to click coordinates to simulate human imprecision
            x_offset = random.randint(-2, 2)
            y_offset = random.randint(-2, 2)
            final_x = max(0, min(self.width, x + x_offset))
            final_y = max(0, min(self.height, y + y_offset))
            
            # Human-like mouse movement with curve
            action.move_by_offset(final_x - 10, final_y - 10)
            action.pause(random.uniform(0.05, 0.2))
            action.move_by_offset(10, 10)
            action.pause(random.uniform(0.05, 0.15))
            action.click()
            action.perform()
            action.reset_actions()
            
            # Random post-click delay
            post_click_delay = random.uniform(0.1, 0.3)
            time.sleep(post_click_delay)
            
            self.click_coordinates = [final_x, final_y]
            log_msg = f"Clicked at coordinates ({final_x}, {final_y}) on: {element_description}"
            self.logger.log(log_msg)
            return log_msg

        @tool
        def right_click(x: int, y: int, element_description: str) -> str:
            """
            Performs a right-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
                element_description: visual description including: element type, text content, size ('big' for instance), color, position relative to other elements
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x, y).context_click().perform()
            action.reset_actions()
            self.click_coordinates = [x, y]
            log_msg = (
                f"Right-clicked at coordinates ({x}, {y}) on: {element_description}"
            )
            self.logger.log(log_msg)
            return log_msg

        @tool
        def double_click(x: int, y: int, element_description: str) -> str:
            """
            Performs a double-click at the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
                element_description: visual description including: element type, text content, size ('big' for instance), color, position relative to other elements
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x, y).double_click().perform()
            action.reset_actions()
            self.click_coordinates = [x, y]
            log_msg = (
                f"Double-clicked at coordinates ({x}, {y}) on: {element_description}"
            )
            self.logger.log(log_msg)
            return log_msg

        @tool
        def move_mouse(x: int, y: int, element_description: str = "") -> str:
            """
            Moves the mouse cursor to the specified coordinates
            Args:
                x: The x coordinate (horizontal position)
                y: The y coordinate (vertical position)
                element_description: Optional visual description of what you're hovering over
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x, y).perform()
            action.reset_actions()
            log_msg = f"Moved mouse to coordinates ({x}, {y})"
            if element_description:
                log_msg += f" over: {element_description}"
            self.logger.log(log_msg)
            return log_msg

        def normalize_text(text):
            return "".join(
                c
                for c in unicodedata.normalize("NFD", text)
                if not unicodedata.combining(c)
            )

        @tool
        def type_text(text: str, target_description: str) -> str:
            """
            Types the specified text at the current cursor position.
            Args:
                text: The text to type
                target_description: Optional visual description of the input field or element where text is being typed (e.g., "search box in the header", "username field in login form")
            """
            import random
            import time
            
            clean_text = normalize_text(text)
            action = ActionChains(self.driver)
            
            # Type with human-like delays between characters
            for char in clean_text:
                action.send_keys(char)
                # Random delay between keystrokes (20-150ms)
                delay = random.uniform(0.02, 0.15)
                action.pause(delay)
                
                # Occasionally pause longer (simulate thinking)
                if random.random() < 0.1:  # 10% chance
                    action.pause(random.uniform(0.2, 0.8))
            
            action.perform()
            action.reset_actions()
            
            # Random delay after typing
            time.sleep(random.uniform(0.1, 0.4))
            
            log_msg = f"Typed text: '{clean_text}' in: {target_description}"
            self.logger.log(log_msg)
            return log_msg

        @tool
        def press_key(key: str, context_description: str) -> str:
            """
            Presses a keyboard key
            Args:
                key: The key to press (e.g. "enter", "space", "backspace", etc.).
                context_description: Optional description of the context or purpose (e.g., "to submit the search form", "to close the modal dialog")
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
            log_msg = f"Pressed key: {key}, context: {context_description}"
            self.logger.log(log_msg)
            return log_msg

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
        def drag_and_drop(
            x1: int,
            y1: int,
            x2: int,
            y2: int,
            source_description: str,
            target_description: str,
        ) -> str:
            """
            Clicks [x1, y1], drags mouse to [x2, y2], then release click.
            Args:
                x1: origin x coordinate
                y1: origin y coordinate
                x2: end x coordinate
                y2: end y coordinate
                source_description: visual description of what you're dragging from
                target_description: visual description of where you're dropping it
            """
            action = ActionChains(self.driver)
            action.move_by_offset(x1, y1).click_and_hold().move_by_offset(
                x2 - x1, y2 - y1
            ).release().perform()
            action.reset_actions()
            message = f"Dragged and dropped from [{x1}, {y1}] to [{x2}, {y2}]"
            message += f" - moved from '{source_description}' to '{target_description}'"
            self.logger.log(message)
            return message

        @tool
        def scroll(
            x: int,
            y: int,
            direction: str,
            amount: int,
        ) -> str:
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

            This tool should be called if you hit a request limit. In that case you should wait for a minute and then try again.
            Args:
                seconds: Number of seconds to wait, generally 3.0 is enough. This is a float, not an integer.
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

    def close(self):
        """Clean up resources"""
        print("Closing browser...")
        self.driver.quit()
        print("Browser closed")
