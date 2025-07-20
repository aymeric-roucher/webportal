"""
Enhanced web crawler with network request interception for API endpoint discovery.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse
import re

from playwright.async_api import async_playwright, Page, ElementHandle, Request, Response
from bs4 import BeautifulSoup


@dataclass
class NetworkRequest:
    """Represents a network request captured during crawling."""
    url: str
    method: str
    headers: Dict[str, str]
    post_data: Optional[str] = None
    response_status: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None
    content_type: Optional[str] = None


@dataclass
class EnhancedWebPageData:
    """Enhanced container for extracted webpage data with network requests."""
    url: str
    title: str
    static_content: str
    dynamic_elements: List[Any]  # Using Any to avoid circular import
    network_requests: List[NetworkRequest]
    api_endpoints: List[Dict[str, Any]]
    markdown_summary: str
    interaction_tools: List[Dict[str, Any]]


class NetworkAwareCrawler:
    """Enhanced web crawler that captures network requests and interactions."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self.network_requests: List[NetworkRequest] = []
        self.api_endpoints: Set[str] = set()
        
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        
        # Set up network request interception
        await self._setup_network_interception()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def _setup_network_interception(self):
        """Set up network request and response interception."""
        self.page.on("request", self._on_request)
        self.page.on("response", self._on_response)
    
    def _on_request(self, request: Request):
        """Handle network requests."""
        url = request.url
        method = request.method
        headers = dict(request.headers)
        post_data = request.post_data
        
        # Check if this looks like an API endpoint
        if self._is_api_endpoint(url, headers):
            self.api_endpoints.add(url)
        
        network_request = NetworkRequest(
            url=url,
            method=method,
            headers=headers,
            post_data=post_data
        )
        self.network_requests.append(network_request)
    
    def _on_response(self, response: Response):
        """Handle network responses."""
        url = response.url
        
        # Find matching request and update with response info
        for request in self.network_requests:
            if request.url == url:
                request.response_status = response.status
                request.response_headers = dict(response.headers)
                request.content_type = response.headers.get("content-type", "")
                break
    
    def _is_api_endpoint(self, url: str, headers: Dict[str, str]) -> bool:
        """Determine if a URL is likely an API endpoint."""
        # Common API patterns
        api_patterns = [
            r'/api/',
            r'/rest/',
            r'/graphql',
            r'/v\d+/',
            r'\.json$',
            r'\.xml$',
        ]
        
        # Check URL patterns
        for pattern in api_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Check content-type headers
        content_type = headers.get("content-type", "").lower()
        if "application/json" in content_type or "application/xml" in content_type:
            return True
        
        # Check for common API headers
        api_headers = ["authorization", "x-api-key", "x-auth-token"]
        for header in api_headers:
            if header in headers:
                return True
        
        return False
    
    async def crawl_with_interactions(self, url: str, wait_time: int = 3000) -> EnhancedWebPageData:
        """
        Crawl a webpage and capture network requests during interactions.
        
        Args:
            url: The URL to crawl
            wait_time: Time to wait for dynamic content to load (ms)
            
        Returns:
            EnhancedWebPageData containing all extracted information
        """
        # Navigate to the page
        await self.page.goto(url, wait_until="networkidle")
        
        # Wait for dynamic content
        await asyncio.sleep(wait_time / 1000)
        
        # Extract basic page info
        title = await self.page.title()
        
        # Extract static content
        static_content = await self._extract_static_content()
        
        # Extract dynamic elements
        dynamic_elements = await self._extract_dynamic_elements()
        
        # Perform some interactions to trigger API calls
        await self._perform_sample_interactions()
        
        # Wait for any triggered requests
        await asyncio.sleep(2000 / 1000)
        
        # Generate interaction tools
        interaction_tools = self._generate_interaction_tools(dynamic_elements)
        
        # Generate markdown summary
        markdown_summary = self._generate_enhanced_markdown(
            url, title, static_content, dynamic_elements, 
            self.network_requests, interaction_tools
        )
        
        return EnhancedWebPageData(
            url=url,
            title=title,
            static_content=static_content,
            dynamic_elements=dynamic_elements,
            network_requests=self.network_requests,
            api_endpoints=list(self.api_endpoints),
            markdown_summary=markdown_summary,
            interaction_tools=interaction_tools
        )
    
    async def _extract_static_content(self) -> str:
        """Extract static content from the page."""
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    async def _extract_dynamic_elements(self) -> List[Dict[str, Any]]:
        """Extract dynamic elements like buttons, forms, links, etc."""
        elements = []
        
        # Extract buttons
        buttons = await self.page.query_selector_all("button, input[type='button'], input[type='submit']")
        for button in buttons:
            element = await self._analyze_element(button, "button")
            if element:
                elements.append(element)
        
        # Extract forms
        forms = await self.page.query_selector_all("form")
        for form in forms:
            form_elements = await self._analyze_form(form)
            elements.extend(form_elements)
        
        # Extract links
        links = await self.page.query_selector_all("a[href]")
        for link in links:
            element = await self._analyze_element(link, "link")
            if element:
                elements.append(element)
        
        # Extract inputs
        inputs = await self.page.query_selector_all("input:not([type='button']):not([type='submit'])")
        for input_elem in inputs:
            element = await self._analyze_element(input_elem, "input")
            if element:
                elements.append(element)
        
        return elements
    
    async def _analyze_element(self, element: ElementHandle, element_type: str) -> Optional[Dict[str, Any]]:
        """Analyze a generic element."""
        try:
            text = await element.inner_text()
            if not text.strip():
                text = await element.get_attribute("value") or await element.get_attribute("aria-label") or element_type.title()
            
            selector = await self._generate_selector(element)
            attributes = await self._get_attributes(element)
            
            result = {
                "type": element_type,
                "selector": selector,
                "text": text.strip(),
                "attributes": attributes,
                "action": "click" if element_type in ["button", "link"] else "input"
            }
            
            # Add type-specific data
            if element_type == "link":
                result["url"] = await element.get_attribute("href")
            elif element_type == "input":
                input_type = await element.get_attribute("type") or "text"
                name = await element.get_attribute("name")
                placeholder = await element.get_attribute("placeholder")
                if name:
                    result["data"] = {name: {"type": input_type, "placeholder": placeholder}}
            
            return result
        except Exception:
            return None
    
    async def _analyze_form(self, form: ElementHandle) -> List[Dict[str, Any]]:
        """Analyze a form element and its inputs."""
        elements = []
        try:
            action = await form.get_attribute("action")
            method = await form.get_attribute("method") or "GET"
            
            # Get form inputs
            inputs = await form.query_selector_all("input, textarea, select")
            form_data = {}
            
            for input_elem in inputs:
                input_type = await input_elem.get_attribute("type") or "text"
                name = await input_elem.get_attribute("name")
                placeholder = await input_elem.get_attribute("placeholder")
                
                if name:
                    form_data[name] = {
                        "type": input_type,
                        "placeholder": placeholder
                    }
            
            selector = await self._generate_selector(form)
            attributes = await self._get_attributes(form)
            
            elements.append({
                "type": "form",
                "selector": selector,
                "text": "Form",
                "attributes": attributes,
                "action": "submit",
                "url": action,
                "method": method,
                "data": form_data
            })
            
        except Exception:
            pass
        
        return elements
    
    async def _generate_selector(self, element: ElementHandle) -> str:
        """Generate a CSS selector for an element."""
        try:
            # Try to get a unique ID first
            element_id = await element.get_attribute("id")
            if element_id:
                return f"#{element_id}"
            
            # Try to get a unique class
            classes = await element.get_attribute("class")
            if classes:
                class_list = classes.split()
                for cls in class_list:
                    if cls and not cls.startswith("js-") and not cls.startswith("ng-"):
                        return f".{cls}"
            
            # Fallback to tag name with position
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            return f"{tag_name}"
            
        except Exception:
            return "element"
    
    async def _get_attributes(self, element: ElementHandle) -> Dict[str, str]:
        """Get all attributes of an element."""
        try:
            return await element.evaluate("""
                el => {
                    const attrs = {};
                    for (let attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            """)
        except Exception:
            return {}
    
    async def _perform_sample_interactions(self):
        """Perform sample interactions to trigger API calls."""
        try:
            # Try to click on some buttons (safely)
            buttons = await self.page.query_selector_all("button:not([disabled])")
            for button in buttons[:3]:  # Limit to first 3 buttons
                try:
                    await button.click()
                    await asyncio.sleep(500 / 1000)  # Wait for potential API calls
                except Exception:
                    continue
            
            # Try to fill some input fields
            inputs = await self.page.query_selector_all("input[type='text'], input[type='email']")
            for input_elem in inputs[:2]:  # Limit to first 2 inputs
                try:
                    await input_elem.fill("test")
                    await asyncio.sleep(500 / 1000)
                except Exception:
                    continue
                    
        except Exception:
            pass
    
    def _generate_interaction_tools(self, dynamic_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate tools for AI agents to interact with the page."""
        tools = []
        
        for elem in dynamic_elements:
            if elem["type"] == "button":
                tools.append({
                    "name": f"click_{elem['text'].lower().replace(' ', '_')}",
                    "description": f"Click the '{elem['text']}' button",
                    "action": "click",
                    "selector": elem["selector"],
                    "type": "button"
                })
            elif elem["type"] == "link":
                tools.append({
                    "name": f"navigate_to_{elem['text'].lower().replace(' ', '_')}",
                    "description": f"Navigate to '{elem['text']}' link",
                    "action": "navigate",
                    "url": elem.get("url"),
                    "type": "link"
                })
            elif elem["type"] == "form":
                tools.append({
                    "name": f"submit_form_{elem['selector'].replace('.', '_').replace('#', '')}",
                    "description": f"Submit the form",
                    "action": "submit",
                    "selector": elem["selector"],
                    "method": elem.get("method", "POST"),
                    "url": elem.get("url"),
                    "data": elem.get("data", {}),
                    "type": "form"
                })
            elif elem["type"] == "input":
                for field_name, field_data in elem.get("data", {}).items():
                    tools.append({
                        "name": f"fill_{field_name}",
                        "description": f"Fill the '{field_name}' input field",
                        "action": "fill",
                        "selector": elem["selector"],
                        "field_name": field_name,
                        "field_type": field_data.get("type", "text"),
                        "placeholder": field_data.get("placeholder"),
                        "type": "input"
                    })
        
        return tools
    
    def _generate_enhanced_markdown(
        self, 
        url: str, 
        title: str, 
        static_content: str, 
        dynamic_elements: List[Dict[str, Any]],
        network_requests: List[NetworkRequest],
        interaction_tools: List[Dict[str, Any]]
    ) -> str:
        """Generate an enhanced markdown summary for AI agents."""
        markdown_parts = []
        
        # Page header
        markdown_parts.append(f"# {title}")
        markdown_parts.append(f"**URL:** {url}\n")
        
        # Static content summary
        markdown_parts.append("## Static Content")
        content_preview = static_content[:500] + "..." if len(static_content) > 500 else static_content
        markdown_parts.append(content_preview + "\n")
        
        # Available tools
        if interaction_tools:
            markdown_parts.append("## Available Tools")
            markdown_parts.append("Use these tools to interact with the page:\n")
            
            for tool in interaction_tools:
                markdown_parts.append(f"### {tool['name']}")
                markdown_parts.append(f"**Description:** {tool['description']}")
                markdown_parts.append(f"**Action:** {tool['action']}")
                
                if tool['action'] == 'click':
                    markdown_parts.append(f"**Selector:** `{tool['selector']}`")
                elif tool['action'] == 'navigate':
                    markdown_parts.append(f"**URL:** {tool['url']}")
                elif tool['action'] == 'submit':
                    markdown_parts.append(f"**Method:** {tool['method']}")
                    markdown_parts.append(f"**URL:** {tool['url']}")
                    if tool.get('data'):
                        markdown_parts.append(f"**Form Fields:** {json.dumps(tool['data'], indent=2)}")
                elif tool['action'] == 'fill':
                    markdown_parts.append(f"**Field:** {tool['field_name']}")
                    markdown_parts.append(f"**Type:** {tool['field_type']}")
                    if tool.get('placeholder'):
                        markdown_parts.append(f"**Placeholder:** {tool['placeholder']}")
                
                markdown_parts.append("")
        
        # API endpoints discovered
        api_requests = [req for req in network_requests if self._is_api_endpoint(req.url, req.headers)]
        if api_requests:
            markdown_parts.append("## API Endpoints Discovered")
            for req in api_requests[:10]:  # Limit to first 10
                markdown_parts.append(f"- **{req.method}** {req.url}")
                if req.response_status:
                    markdown_parts.append(f"  - Status: {req.response_status}")
                if req.content_type:
                    markdown_parts.append(f"  - Content-Type: {req.content_type}")
                markdown_parts.append("")
        
        # Dynamic elements summary
        if dynamic_elements:
            markdown_parts.append("## Interactive Elements Found")
            by_type = {}
            for elem in dynamic_elements:
                if elem["type"] not in by_type:
                    by_type[elem["type"]] = []
                by_type[elem["type"]].append(elem)
            
            for elem_type, elements in by_type.items():
                markdown_parts.append(f"### {elem_type.title()}s ({len(elements)})")
                for elem in elements[:5]:  # Limit to first 5 of each type
                    markdown_parts.append(f"- {elem['text']}")
                if len(elements) > 5:
                    markdown_parts.append(f"- ... and {len(elements) - 5} more")
                markdown_parts.append("")
        
        return "\n".join(markdown_parts)


async def crawl_with_network(url: str, output_file: str = None, headless: bool = True) -> EnhancedWebPageData:
    """
    Convenience function to crawl a website with network interception.
    
    Args:
        url: The URL to crawl
        output_file: Optional file path to save the markdown summary
        headless: Whether to run browser in headless mode
        
    Returns:
        EnhancedWebPageData containing all extracted information
    """
    async with NetworkAwareCrawler(headless=headless) as crawler:
        data = await crawler.crawl_with_interactions(url)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data.markdown_summary)
        
        return data 