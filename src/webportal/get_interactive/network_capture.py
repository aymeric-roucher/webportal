import os
import json
import time
import requests
from typing import Any
from urllib.parse import urlparse

from smolagents import CodeAgent
from smolagents.memory import ActionStep

from webportal.get_interactive.selenium_agent import SeleniumVisionAgent

class SeleniumNetworkCaptureAgent(SeleniumVisionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize network request tracking
        self.network_requests = []
        self.step_requests = {}  # step_number -> list of requests for that step
        self._setup_network_monitoring()

    def setup_step_callbacks(self) -> None:
        self._setup_step_callbacks(
            [self.take_screenshot_callback, self.capture_requests_callback]
        )

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
        time.sleep(1) # making sure the response is received
        logs = self.driver.get_log("performance")

        if not logs:
            return []

        # Temporary storage for this step's requests and responses
        requests_map = {}
        responses_map = {}

        # Process new logs only
        for log in logs:
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
                        response_data["base64Encoded"] = body_result.get(
                            "base64Encoded", False
                        )
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

    def capture_requests_callback(
        self, memory_step: ActionStep | None = None, agent: CodeAgent | None = None
    ) -> None:
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

    def _analyze_step_requests(
        self,
        step_number: int,
        requests: list[dict[str, Any]],
        memory_step: ActionStep | None = None,
    ):
        """Analyze requests from a specific step and generate markdown summaries"""

        # Filter requests to get JSON and HTML responses separately
        json_requests, html_requests = self._filter_relevant_requests(requests)

        if not json_requests and not html_requests:
            return

        print(f"\n=== STEP {step_number} REQUEST ANALYSIS ===")
        print(
            f"Found {len(json_requests)} JSON requests and {len(html_requests)} HTML requests"
        )

        # Get the action that was performed in this step
        action_description = self._get_step_action_description(memory_step)
        tool_call_info = self._get_tool_call_info(memory_step)

        # Generate markdown for this step
        markdown_summary = self._generate_step_markdown(
            step_number,
            action_description,
            tool_call_info,
            json_requests,
            html_requests,
        )

        if markdown_summary:
            self._save_step_markdown(step_number, markdown_summary)

    def _get_step_action_description(
        self, memory_step: ActionStep | None = None
    ) -> str:
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

    def _get_tool_call_info(
        self, memory_step: ActionStep | None = None
    ) -> dict[str, Any]:
        """Extract tool call information for markdown generation"""
        if memory_step and memory_step.tool_calls:
            tool_call = memory_step.tool_calls[0]
            return {
                "tool_name": tool_call.name,
                "arguments": getattr(tool_call, "arguments", {}),
            }
        return {"tool_name": "unknown", "arguments": {}}

    def _generate_step_markdown(
        self,
        step_number: int,
        action_description: str,
        tool_call_info: dict[str, Any],
        json_requests: list[dict[str, Any]],
        html_requests: list[dict[str, Any]],
    ) -> str:
        """Generate markdown summary for a step in the interactive_element format"""

        if not json_requests and not html_requests:
            return ""

        # Try to infer element type from action
        element_type = self._infer_element_type(tool_call_info, action_description)

        # Get current page location (simplified)
        current_url = self.driver.current_url if hasattr(self, "driver") else "unknown"
        location_page = self._extract_location_page(current_url)

        markdown = f"""```interactive_element_step_{step_number}
location_page: {location_page}
type: {element_type}
visual_element: {action_description}
trigger: {tool_call_info["tool_name"]} with args {tool_call_info["arguments"]}
"""

        # Generate separate markdown sections for JSON and HTML requests
        if json_requests:
            markdown += self._generate_json_requests_section(
                json_requests, action_description
            )

        if html_requests:
            markdown += self._generate_html_requests_section(
                html_requests, action_description
            )

        # Add viewport effect
        viewport_effect = self._describe_viewport_effect(action_description)
        markdown += f"viewport_effect: {viewport_effect}\n"

        markdown += "```\n"
        return markdown

    def _generate_json_requests_section(
        self, json_requests: list[dict[str, Any]], action_description: str
    ) -> str:
        """Generate markdown section for JSON API requests"""
        section = ""

        for i, request in enumerate(json_requests):
            url = request.get("url", "")
            method = request.get("method", "GET")

            if i == 0:  # Primary request
                section += f"request: {method} {url}\n"

                # Add request arguments if it's a POST with data
                post_data = request.get("post_data", "")
                if post_data and method in ["POST", "PUT", "PATCH"]:
                    section += f"arguments:\n"
                    try:
                        json_data = json.loads(post_data)
                        # Truncate large JSON for readability
                        json_str = json.dumps(json_data)
                        if len(json_str) > 500:
                            json_str = json_str[:500] + "..."
                        section += f'  "body" (json): {json_str}\n'
                    except json.JSONDecodeError:
                        post_data_truncated = post_data[:200] + (
                            "..." if len(post_data) > 200 else ""
                        )
                        section += f'  "body" (raw): {post_data_truncated}\n'

                # Add effect description
                effect = self._describe_request_effect(request, action_description)
                section += f"effect: {effect}\n"

            # Add response details for all JSON requests
            response_data = request.get("response", {})
            response_body = response_data.get("body", "")

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
                            if "data" in json_response:
                                data_info = self._describe_data_field(
                                    json_response["data"]
                                )
                                section += f"  data: {data_info}\n"

                            if "errors" in json_response:
                                section += f"  has_errors: true\n"

                            # Look for pagination info
                            if any(
                                key in json_response
                                for key in ["pageInfo", "pagination", "hasNextPage"]
                            ):
                                section += f"  has_pagination: true\n"

                            # Look for common GraphQL/API patterns
                            if "nodes" in json_response:
                                nodes_info = self._describe_nodes_field(
                                    json_response["nodes"]
                                )
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

    def _generate_html_requests_section(
        self, html_requests: list[dict[str, Any]], action_description: str
    ) -> str:
        """Generate markdown section for HTML page requests"""
        section = ""

        for i, request in enumerate(html_requests):
            url = request.get("url", "")
            method = request.get("method", "GET")

            if i == 0:  # Primary request
                section += f"request: {method} {url}\n"

                # Add request arguments if it's a POST with data
                post_data = request.get("post_data", "")
                if post_data and method in ["POST", "PUT", "PATCH"]:
                    section += f"arguments:\n"
                    section += f'  "body" (form-data): {post_data[:200]}...\n'

                # Add effect description
                effect = self._describe_request_effect(request, action_description)
                section += f"effect: {effect}\n"
                section += f"returns: HTML page content\n"

            # Add HTML response analysis
            response_data = request.get("response", {})
            response_body = response_data.get("body", "")

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
                        html_indicators.append("search_page")
                    if 'class="issue' in response_body.lower():
                        html_indicators.append("issues_page")
                    if 'class="repository' in response_body.lower():
                        html_indicators.append("repository_page")
                    if "<form" in response_body.lower():
                        html_indicators.append("has_forms")
                    if "data-" in response_body.lower():
                        html_indicators.append("has_data_attributes")

                    if html_indicators:
                        section += f"  page_indicators: {html_indicators}\n"

                    # Extract some key content hints for LLM
                    content_preview = (
                        response_body[:1000].replace("\n", " ").replace("\t", " ")
                    )
                    # Clean up multiple spaces
                    import re

                    content_preview = re.sub(r"\s+", " ", content_preview)
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

    def _infer_element_type(
        self, tool_call_info: dict[str, Any], action_description: str
    ) -> str:
        """Infer the UI element type from the action"""
        tool_name = tool_call_info.get("tool_name", "")

        if tool_name == "click":
            if "button" in action_description.lower():
                return "Button"
            elif (
                "dropdown" in action_description.lower()
                or "select" in action_description.lower()
            ):
                return "Button/Dropdown"
            elif "link" in action_description.lower():
                return "Link"
            else:
                return "Clickable Element"
        elif tool_name == "type_text":
            return "Input Field"
        elif tool_name == "scroll":
            return "Scrollable Area"
        else:
            return "Interactive Element"

    def _extract_location_page(self, url: str) -> str:
        """Extract a meaningful location page identifier from URL"""
        if not url or url == "unknown":
            return "unknown_page"

        parsed = urlparse(url)
        path = parsed.path.strip("/")

        # Handle GitHub-style URLs
        if "github.com" in parsed.netloc:
            path_parts = path.split("/")
            if len(path_parts) >= 2:
                return f"{path_parts[0]}/{path_parts[1]}/{'/'.join(path_parts[2:])}"

        return path if path else parsed.netloc

    def _describe_request_effect(
        self, request: dict[str, Any], action_description: str
    ) -> str:
        """Describe what effect the request has"""
        method = request.get("method", "GET")
        url = request.get("url", "")

        if method == "GET":
            if "search" in url.lower():
                return f"Performs search based on {action_description}"
            elif "sort" in url.lower():
                return f"Sorts content based on {action_description}"
            elif "filter" in url.lower():
                return f"Filters content based on {action_description}"
            else:
                return f"Retrieves data triggered by {action_description}"
        else:
            return f"Submits data from {action_description}"

    def _describe_viewport_effect(self, action_description: str) -> str:
        """Describe the visual effect on the viewport"""
        if "click" in action_description:
            if "sort" in action_description.lower():
                return "Updates the content display with new sort order"
            elif "filter" in action_description.lower():
                return "Updates the content display with filtered results"
            elif "search" in action_description.lower():
                return "Updates the page with search results"
            else:
                return "Updates the page content or navigation"
        elif "type" in action_description:
            return "Updates input field with typed text"
        elif "scroll" in action_description:
            return "Changes visible content area"
        else:
            return "Modifies page display or interaction state"

    def _save_step_markdown(self, step_number: int, markdown: str):
        """Save the markdown summary for a step"""
        filename = f"step_{step_number:03d}_interactive_element.md"
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, "w") as f:
            f.write(markdown)

        print(f"💾 Saved interactive element summary to: {filepath}")
