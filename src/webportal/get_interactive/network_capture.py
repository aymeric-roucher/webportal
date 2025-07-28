import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from smolagents import CodeAgent
from smolagents.memory import ActionStep

from webportal.get_interactive.selenium_agent import PlaywrightVisionAgent
from webportal.utils import describe_response_format


class PlaywrightNetworkCaptureAgent(PlaywrightVisionAgent):
    def __init__(
        self,
        *args,
        markdown_file_path: Path | None = None,
        domain_to_stay_on: str | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.network_requests: list[dict[str, Any]] = []
        self.step_requests: dict[int, list[dict[str, Any]]] = {}
        self.previous_url: str | None = None

        self.markdown_file_path = (
            markdown_file_path or Path(self.data_dir) / "interactive_elements.md"
        )
        self.domain_to_stay_on = domain_to_stay_on
        self._initialize_markdown_file()

        self._setup_network_monitoring()

    def setup_step_callbacks(self) -> None:
        self._setup_step_callbacks(
            [self.take_screenshot_callback, self.capture_requests_callback]
        )

    def _setup_network_monitoring(self):
        """Setup Playwright network monitoring"""
        # Clear any existing network requests
        self.network_requests = []
        self.request_response_map = {}
        
        # Set up request and response listeners
        self.page.on('request', self._on_request)
        self.page.on('response', self._on_response)
        
        print("Network monitoring enabled")
        
    def _on_request(self, request):
        """Handle request events"""
        request_data = {
            'timestamp': time.time(),
            'url': request.url,
            'method': request.method,
            'headers': request.headers,
            'post_data': request.post_data if request.method == 'POST' else '',
            'request_id': id(request),
            'type': request.resource_type,
        }
        self.request_response_map[id(request)] = request_data
        
    def _on_response(self, response):
        """Handle response events"""
        request_id = id(response.request)
        if request_id in self.request_response_map:
            request_data = self.request_response_map[request_id]
            try:
                # Get response body
                body = response.body() if response.status < 400 else None
                body_text = body.decode('utf-8') if body else None
            except Exception:
                body_text = None
                
            request_data['response'] = {
                'status_code': response.status,
                'status_text': response.status_text,
                'headers': response.headers,
                'url': response.url,
                'body': body_text,
                'response_timestamp': time.time(),
            }

    def _initialize_markdown_file(self):
        """Initialize the centralized markdown file at the beginning of the agent session"""
        header = """# Interactive Elements Analysis"""

        self.markdown_file_path.write_text(header)
        print(f"📝 Initialized markdown file: {self.markdown_file_path}")

    def capture_step_network_activity(self, step_number: int) -> list[dict[str, Any]]:
        """Capture network activity that happened during a specific step"""
        # Wait a bit to ensure all responses are received
        time.sleep(1)
        
        # Get requests from the current step by filtering from our collected requests
        step_requests = []
        current_time = time.time()
        
        for request_data in self.request_response_map.values():
            # Add step number to request data
            request_data['step_number'] = step_number
            step_requests.append(request_data.copy())
        
        # Store step requests for later analysis
        self.step_requests[step_number] = step_requests
        
        # Clear the request map for the next step
        self.request_response_map = {}
        
        return step_requests

    def capture_requests_callback(
        self, memory_step: ActionStep, agent: CodeAgent
    ) -> None:
        """Callback that captures the requests for a step"""
        # Capture network requests for this specific step
        current_step = memory_step.step_number if memory_step else 0
        self.logger.log(f"Capturing network requests for step {current_step}")

        step_requests = self.capture_step_network_activity(current_step)
        if step_requests:
            capture_message = f"Captured {len(step_requests)} network requests for step {current_step}"
        else:
            capture_message = "No network requests captured for this step"
        self.logger.log(capture_message)
        if isinstance(memory_step.observations, str):
            memory_step.observations += f"\n{capture_message}"
        else:
            memory_step.observations = capture_message

        current_url = self.page.url
        if self.domain_to_stay_on:
            from urllib.parse import urlparse

            current_domain = urlparse(current_url).netloc
            base_domain = self.domain_to_stay_on.replace("www.", "").replace(".", "-")
            if base_domain not in current_domain.replace(
                ".", "-"
            ):  # We allow domain like arxiv-org.atlassian.net for base domain arxiv.org
                raise Exception(
                    f"Visited {current_url}, out of domain {self.domain_to_stay_on}: interrupting agent"
                )

        memory_step.observations += (
            f"\nBrowser is currently at this url: {self.page.url}\n"
        )


        # Always analyze the step (even if no requests) to capture agent context
        self._analyze_step_requests(current_step, step_requests, memory_step)

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
                request_type
                in [
                    "XHR",
                    "Fetch",
                    "Document",
                ]  # Include Document type for initial page loads
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
                    if request["response"].get("body"):
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
        return (
            relevant_requests_filtered_by_json_body,
            relevant_requests_filtered_by_html_body,
        )

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
        browser_cookies = self.context.cookies()
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
            "referer": self.page.url,
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

    def _analyze_step_requests(
        self, step_number: int, requests: list[dict[str, Any]], memory_step: ActionStep
    ):
        """Analyze requests from a specific step and generate markdown summaries"""

        # Filter requests to get JSON and HTML responses separately
        json_requests, html_requests = self._filter_relevant_requests(requests)

        self.logger.log(f"\n=== STEP {step_number} REQUEST ANALYSIS ===")
        if json_requests or html_requests:
            self.logger.log(
                f"Found {len(json_requests)} JSON requests and {len(html_requests)} HTML requests"
            )
        else:
            self.logger.log("No relevant network requests found for this step")

        # Get the action that was performed in this step
        tool_call_info = self._get_tool_call_info(memory_step)

        # Get agent's step context (observations and reasoning)
        model_output = memory_step.model_output if memory_step else ""

        # Generate markdown for this step (including agent context even if no requests)
        markdown_summary = self._generate_step_interaction_summary_markdown(
            tool_call_info=tool_call_info,
            json_requests=json_requests,
            html_requests=html_requests,
            previous_url=self.previous_url,
        )

        # Always save step markdown (even if no requests) to include agent context
        self._save_step_markdown(
            step_number=step_number,
            markdown=markdown_summary,
            output_model=model_output,
        )
        self.previous_url = self.page.url

    def _get_tool_call_info(self, memory_step: ActionStep) -> dict[str, Any]:
        """Extract tool call information for markdown generation"""
        if memory_step.tool_calls:
            tool_call = memory_step.tool_calls[0]
            return {
                "name": tool_call.name,
                "arguments": tool_call.arguments,
            }
        else:
            return {"name": "unknown", "arguments": {}}

    def _generate_step_interaction_summary_markdown(
        self,
        tool_call_info: dict[str, Any],
        json_requests: list[dict[str, Any]],
        html_requests: list[dict[str, Any]],
        previous_url: str | None = None,
    ) -> str:
        """Generate markdown summary for a step with individual blocks per request"""

        # Get current page location

        # Combine all requests for processing
        all_requests = json_requests + html_requests
        markdown_blocks = []

        # Only add request blocks if there are actual requests
        if all_requests:
            for request in all_requests:
                block = self._generate_individual_request_block(
                    request=request,
                    tool_call_info=tool_call_info,
                    previous_url=previous_url,
                )
                if block:
                    markdown_blocks.append(block)

        return "\n\n".join(markdown_blocks) if markdown_blocks else ""

    def _generate_individual_request_block(
        self,
        request: dict[str, Any],
        tool_call_info: dict[str, Any],
        previous_url: str | None = None,
    ) -> str:
        """Generate an individual markdown block for a single request"""

        url = request["url"]
        method = request["method"]
        response = request["response"]
        response_body = response["body"] if response else ""

        # Extract base URL without query parameters
        base_url = self._extract_base_url(url)

        # Simple block name from URL path
        block_name = self._generate_simple_block_name(url)

        # Extract arguments
        arguments = self._extract_request_arguments(request)

        # Simple descriptions
        returns = describe_response_format(response_body)

        # Build the markdown block with minimal inference
        markdown = f"```interactive_element_{block_name}\n"
        markdown += f"location_page: {previous_url}\n"
        trigger_description = tool_call_info["name"]
        if "element_description" in tool_call_info["arguments"]:
            trigger_description += (
                f" on {tool_call_info['arguments']['element_description']}"
            )
        markdown += f"trigger: {trigger_description}\n"
        markdown += f"request: {method} {base_url}\n"

        if arguments:
            markdown += f"arguments: {arguments}\n"

        markdown += f"returns: {returns}\n"
        markdown += "```"

        return markdown

    def _save_step_markdown(self, step_number: int, markdown: str, output_model: str):
        """Append the markdown summary for a step to the centralized file"""
        step_header = f"\n## Step {step_number}\n\n"

        # Add agent context section
        agent_section = ""
        if output_model:
            agent_section += f"**Agent output:**\n```\n{output_model}\n```\n\n"

        markdown_section = ""
        if markdown:
            markdown_section = f"**Network requests:**\n\n{markdown}\n\n"
        else:
            markdown_section = (
                "**Network requests:**\n\nNo significant activity in this step.\n\n"
            )

        with self.markdown_file_path.open("a") as f:
            f.write(step_header)
            if agent_section:
                f.write(agent_section)
            if markdown_section:
                f.write(markdown_section)
                f.write("\n\n")
            elif not agent_section:
                f.write("No significant activity in this step.\n\n")

        print(
            f"💾 Appended step {step_number} to markdown file: {self.markdown_file_path}"
        )

    def _extract_request_arguments(self, request: dict[str, Any]) -> str:
        """Extract arguments from request (POST data or URL parameters)"""
        method = request.get("method", "GET")
        url = request.get("url", "")
        post_data = request.get("post_data", "")

        arguments = []

        # Handle POST data
        if method == "POST" and post_data:
            try:
                # Try to parse as JSON first
                json_data = json.loads(post_data)
                if isinstance(json_data, dict):
                    formatted_json = json.dumps(json_data, indent=2)
                    arguments.append(f'"body" (JSON): \n{formatted_json}')
                else:
                    arguments.append(f'"body": {json.dumps(json_data)}')
            except json.JSONDecodeError:
                # Handle form data or other formats
                if "multipart/form-data" in str(request.get("headers", {})):
                    arguments.append('"body" (form-data): [multipart form data]')
                elif "application/x-www-form-urlencoded" in str(
                    request.get("headers", {})
                ):
                    arguments.append(
                        f'"body" (url-encoded): {post_data[:200]}...'
                        if len(post_data) > 200
                        else f'"body" (url-encoded): {post_data}'
                    )
                else:
                    arguments.append(
                        f'"body": {post_data[:200]}...'
                        if len(post_data) > 200
                        else f'"body": {post_data}'
                    )

        # Handle URL parameters - specifically for GraphQL queries in GET requests
        if "?" in url:
            from urllib.parse import parse_qs, unquote, urlparse

            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            # Special handling for GraphQL queries passed as URL parameters
            if "body" in params and "_graphql" in url:
                try:
                    # Decode the URL-encoded body parameter
                    body_param = unquote(params["body"][0])
                    json_data = json.loads(body_param)
                    formatted_json = json.dumps(json_data, indent=2)
                    arguments.append(f'"body" (url-encoded): \n{formatted_json}')
                except (json.JSONDecodeError, KeyError, IndexError):
                    # Fallback to regular parameter handling
                    param_strs = []
                    for key, values in params.items():
                        if len(values) == 1:
                            param_strs.append(f'{key}="{values[0]}"')
                        else:
                            param_strs.append(f"{key}={values}")
                    arguments.append(f"params: {', '.join(param_strs)}")
            else:
                # Regular URL parameter handling
                param_strs = []
                for key, values in params.items():
                    if len(values) == 1:
                        param_strs.append(f'{key}="{values[0]}"')
                    else:
                        param_strs.append(f"{key}={values}")
                arguments.append(f"params: {', '.join(param_strs)}")

        return "\n".join(arguments) if arguments else ""

    def _extract_base_url(self, url: str) -> str:
        """Extract base URL without query parameters"""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        # Reconstruct URL without query parameters
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return base_url

    def _generate_simple_block_name(self, url: str) -> str:
        """Generate a simple block name from URL"""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]

        # Simple patterns
        if "_graphql" in url:
            return "_graphql"
        elif "search" in url:
            return "search"
        elif "hovercard" in url:
            return "hovercard"
        elif len(path_parts) >= 2:
            return f"{path_parts[-1]}"
        else:
            return "request"


# Compatibility alias for existing code
SeleniumNetworkCaptureAgent = PlaywrightNetworkCaptureAgent
