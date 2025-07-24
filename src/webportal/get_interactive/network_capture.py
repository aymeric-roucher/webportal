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
        """Generate markdown summary for a step with individual blocks per request"""

        if not json_requests and not html_requests:
            return ""

        # Get current page location
        current_url = self.driver.current_url if hasattr(self, "driver") else "unknown"
        location_page = self._extract_location_page(current_url)
        
        # Combine all requests for processing
        all_requests = json_requests + html_requests
        markdown_blocks = []
        
        for request in all_requests:
            block = self._generate_individual_request_block(
                request, action_description, tool_call_info, location_page, step_number
            )
            if block:
                markdown_blocks.append(block)
        
        return "\n\n".join(markdown_blocks)

    def _generate_individual_request_block(
        self,
        request: dict[str, Any],
        action_description: str,
        tool_call_info: dict[str, Any],
        location_page: str,
        step_number: int,
    ) -> str:
        """Generate an individual markdown block for a single request"""
        
        url = request.get("url", "")
        method = request.get("method", "GET")
        response = request.get("response", {})
        response_body = response.get("body", "") if response else ""
        
        # Simple block name from URL path
        block_name = self._generate_simple_block_name(url)
        
        # Extract arguments
        arguments = self._extract_request_arguments(request)
        
        # Simple descriptions
        returns = self._describe_response_format(response_body)
        
        # Build the markdown block with minimal inference
        markdown = f"```interactive_element_{block_name}\n"
        markdown += f"location_page: {location_page}\n"
        markdown += f"type: \n"  # Leave empty for LLM to fill
        markdown += f"visual_element: \n"  # Leave empty for LLM to fill
        markdown += f"trigger: \n"  # Leave empty for LLM to fill
        markdown += f"request: {method} {url}\n"
        
        if arguments:
            markdown += f"arguments: {arguments}\n"
        
        markdown += f"effect: \n"  # Leave empty for LLM to fill
        markdown += f"returns: {returns}\n"
        markdown += f"viewport_effect: \n"  # Leave empty for LLM to fill
        markdown += "```"
        
        return markdown

    def _generate_json_requests_section(
        self, json_requests: list[dict[str, Any]], action_description: str
    ) -> str:
        """Generate markdown section for JSON API requests"""
        if not json_requests:
            return ""
        
        markdown = ""
        for i, request in enumerate(json_requests):
            url = request.get("url", "")
            method = request.get("method", "GET")
            post_data = request.get("post_data", "")
            response = request.get("response", {})
            response_body = response.get("body", "") if response else ""
            
            # Extract arguments from POST data or URL parameters
            arguments = self._extract_request_arguments(request)
            
            # Determine effect and returns
            effect = self._infer_request_effect(action_description, url, response_body)
            returns = self._describe_response_format(response_body)
            
            if i > 0:
                markdown += "\n"
            
            markdown += f"request: {method} {url}\n"
            if arguments:
                markdown += f"arguments: {arguments}\n"
            markdown += f"effect: {effect}\n"
            markdown += f"returns: {returns}\n"
        
        return markdown


    def _generate_html_requests_section(
        self, html_requests: list[dict[str, Any]], action_description: str
    ) -> str:
        """Generate markdown section for HTML page requests"""
        if not html_requests:
            return ""
        
        markdown = ""
        for i, request in enumerate(html_requests):
            url = request.get("url", "")
            method = request.get("method", "GET")
            response = request.get("response", {})
            response_body = response.get("body", "") if response else ""
            
            # Extract arguments from URL parameters
            arguments = self._extract_request_arguments(request)
            
            # Determine effect and returns for HTML requests
            effect = self._infer_request_effect(action_description, url, response_body)
            returns = "HTML page content"
            
            if i > 0:
                markdown += "\n"
            
            markdown += f"request: {method} {url}\n"
            if arguments:
                markdown += f"arguments: {arguments}\n"
            markdown += f"effect: {effect}\n"
            markdown += f"returns: {returns}\n"
        
        return markdown

    def _save_step_markdown(self, step_number: int, markdown: str):
        """Save the markdown summary for a step"""
        filename = f"step_{step_number:03d}_interactive_element.md"
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, "w") as f:
            f.write(markdown)

        print(f"💾 Saved interactive element summary to: {filepath}")

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
                elif "application/x-www-form-urlencoded" in str(request.get("headers", {})):
                    arguments.append(f'"body" (url-encoded): {post_data[:200]}...' if len(post_data) > 200 else f'"body" (url-encoded): {post_data}')
                else:
                    arguments.append(f'"body": {post_data[:200]}...' if len(post_data) > 200 else f'"body": {post_data}')
        
        # Handle URL parameters - specifically for GraphQL queries in GET requests
        if "?" in url:
            from urllib.parse import urlparse, parse_qs, unquote
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
                            param_strs.append(f'{key}={values}')
                    arguments.append(f"URL params: {', '.join(param_strs)}")
            else:
                # Regular URL parameter handling
                param_strs = []
                for key, values in params.items():
                    if len(values) == 1:
                        param_strs.append(f'{key}="{values[0]}"')
                    else:
                        param_strs.append(f'{key}={values}')
                arguments.append(f"URL params: {', '.join(param_strs)}")
        
        return "\n".join(arguments) if arguments else ""


    def _describe_response_format(self, response_body: str) -> str:
        """Describe the format and content of the response"""
        if not response_body:
            return "Empty response"
        
        try:
            # Try to parse as JSON
            json_data = json.loads(response_body)
            if isinstance(json_data, dict):
                # Analyze JSON structure
                keys = list(json_data.keys())
                if "data" in keys:
                    return "JSON with data object containing structured information"
                elif "results" in keys or "items" in keys:
                    return "JSON with results array containing search/list data"
                elif "payload" in keys:
                    return "JSON with payload containing response data"
                else:
                    return f"JSON object with keys: {', '.join(keys[:5])}" + ("..." if len(keys) > 5 else "")
            elif isinstance(json_data, list):
                return f"JSON array with {len(json_data)} items"
            else:
                return "JSON response"
        except json.JSONDecodeError:
            if "DOCTYPE" in response_body:
                return "HTML page content"
            else:
                return "Text/other format response"


    def _extract_location_page(self, url: str) -> str:
        """Extract a simplified page location from URL"""
        from urllib.parse import urlparse
        
        if not url or url == "unknown":
            return "unknown"
        
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        
        if not path:
            return "home"
        
        # Simplify common GitHub patterns
        path_parts = path.split("/")
        if len(path_parts) >= 2:
            return f"^{path_parts[0]}/{path_parts[1]}" + ("/" + "/".join(path_parts[2:]) if len(path_parts) > 2 else "")
        else:
            return f"^{path}"


    def _generate_simple_block_name(self, url: str) -> str:
        """Generate a simple block name from URL"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        
        # Simple patterns
        if "_graphql" in url:
            return "graphql_request"
        elif "search" in url:
            return "search"
        elif "hovercard" in url:
            return "hovercard"
        elif len(path_parts) >= 2:
            return f"{path_parts[-1]}"
        else:
            return "request"

    def generate_complete_markdown_documentation(self, output_file: str = None) -> str:
        """Generate a complete markdown documentation file from all captured requests"""
        if not self.step_requests:
            return "No requests captured to generate documentation."
        
        markdown_sections = []
        
        for step_number, requests in self.step_requests.items():
            if not requests:
                continue
                
            # Get step action information
            memory_step = None  # You might need to store this if you want full action info
            action_description = f"step {step_number} action"
            tool_call_info = {"tool_name": "unknown", "arguments": {}}
            
            # Filter requests
            json_requests, html_requests = self._filter_relevant_requests(requests)
            
            if not json_requests and not html_requests:
                continue
            
            # Generate markdown for this step
            current_url = self.driver.current_url if hasattr(self, "driver") else "unknown"
            location_page = self._extract_location_page(current_url)
            element_type = self._infer_element_type(tool_call_info, action_description)
            
            step_markdown = f"""```interactive_element_step_{step_number}
location_page: {location_page}
type: {element_type}
visual_element: {action_description}
trigger: {tool_call_info["tool_name"]} with args {tool_call_info["arguments"]}
"""
            
            # Add JSON requests
            if json_requests:
                step_markdown += self._generate_json_requests_section(json_requests, action_description)
            
            # Add HTML requests
            if html_requests:
                step_markdown += self._generate_html_requests_section(html_requests, action_description)
            
            # Add viewport effect
            viewport_effect = self._describe_viewport_effect(action_description)
            step_markdown += f"viewport_effect: {viewport_effect}\n"
            step_markdown += "```\n"
            
            markdown_sections.append(step_markdown)
        
        complete_markdown = "\n\n".join(markdown_sections)
        
        # Save to file if specified
        if output_file:
            with open(output_file, "w") as f:
                f.write(complete_markdown)
            print(f"💾 Saved complete documentation to: {output_file}")
        
        return complete_markdown
