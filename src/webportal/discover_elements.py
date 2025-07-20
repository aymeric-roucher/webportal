import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright, Page, Response
from dataclasses import dataclass


@dataclass
class InteractiveElement:
    """Represents an interactive element found on the page"""
    element_id: str
    element_type: str
    visual_element: str
    trigger: str
    selector: str
    requests: List[Dict[str, Any]]
    effect: str
    returns: str
    viewport_effect: str


class WebPageAnalyzer:
    """Analyzes web pages to discover interactive elements and their API calls"""
    
    def __init__(self):
        self.captured_requests: List[Dict[str, Any]] = []
        self.page_content: str = ""
        self.interactive_elements: List[InteractiveElement] = []
        
    async def analyze_page(self, url: str, output_file: Optional[str] = None) -> str:
        """Analyze a webpage and generate markdown documentation"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # Headless for performance
            context = await browser.new_context()
            page = await context.new_page()
            
            # Set up request/response intercepting
            page.on('request', self._capture_request)
            page.on('response', self._capture_response)
            
            try:
                # Navigate to the page
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(1000)  # Wait for dynamic content
                
                # Get static content
                self.page_content = await page.content()
                
                # Discover interactive elements
                await self._discover_interactive_elements(page)
                
                # Generate markdown
                markdown_content = self._generate_markdown(url)
                
                if output_file:
                    Path(output_file).write_text(markdown_content)
                    
                return markdown_content
                
            finally:
                await browser.close()
    
    async def _discover_interactive_elements(self, page: Page):
        """Discover and analyze interactive elements on the page"""
        # Common interactive selectors
        interactive_selectors = [
            'button',
            'a[href]',
            '[role="button"]',
            '[onclick]',
            'input[type="submit"]',
            'input[type="button"]',
            '.btn, .button',
            '[data-action]',
            '[data-click]',
            'select',
            '.dropdown',
            '.filter',
            '.sort',
            '.toggle'
        ]
        
        for selector in interactive_selectors:
            elements = await page.query_selector_all(selector)
            
            # Limit to first 5 elements per selector type for performance
            for element in elements[:5]:
                await self._analyze_element(page, element, selector)
    
    async def _analyze_element(self, page: Page, element, selector: str):
        """Analyze a specific element for interactions"""
        try:
            # Clear captured requests before interaction
            initial_request_count = len(self.captured_requests)
            
            # Get element info
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            text_content = await element.evaluate('el => el.textContent?.trim() || ""')
            class_name = await element.evaluate('el => el.className || ""')
            
            # Skip if element is not visible or has no meaningful content
            is_visible = await element.is_visible()
            if not is_visible or (not text_content and not class_name):
                return
            
            # Try different interaction types
            interactions_to_try = ['click', 'hover']
            
            for interaction_type in interactions_to_try:
                try:
                    if interaction_type == 'click':
                        await element.click(timeout=5000)
                    elif interaction_type == 'hover':
                        await element.hover(timeout=5000)
                    
                    # Wait for potential network requests
                    await page.wait_for_timeout(1000)
                    
                    # Check if new requests were captured
                    new_requests = self.captured_requests[initial_request_count:]
                    
                    if new_requests:
                        # Create interactive element
                        element_id = f"interactive_element_{len(self.interactive_elements)}"
                        
                        # Determine element type and visual description
                        element_type = self._determine_element_type(tag_name, class_name, text_content)
                        visual_element = self._describe_visual_element(text_content, class_name, tag_name)
                        effect = self._describe_effect(new_requests, text_content)
                        returns = self._describe_returns(new_requests)
                        
                        interactive_el = InteractiveElement(
                            element_id=element_id,
                            element_type=element_type,
                            visual_element=visual_element,
                            trigger=interaction_type.capitalize(),
                            selector=selector,
                            requests=new_requests,
                            effect=effect,
                            returns=returns,
                            viewport_effect="none"  # Could be enhanced to detect viewport changes
                        )
                        
                        self.interactive_elements.append(interactive_el)
                        
                        # Update the initial count for next interaction
                        initial_request_count = len(self.captured_requests)
                        
                except Exception as e:
                    # Continue with other elements if one fails
                    continue
                    
        except Exception as e:
            # Skip problematic elements
            pass
    
    def _capture_request(self, request):
        """Capture outgoing requests"""
        # Filter out common resource requests
        if any(ext in request.url for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.ico', '.woff']):
            return
            
        request_data = {
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'post_data': request.post_data
        }
        self.captured_requests.append(request_data)
    
    def _capture_response(self, response: Response):
        """Capture response data"""
        # Could be enhanced to capture response bodies
        pass
    
    def _determine_element_type(self, tag_name: str, class_name: str, text_content: str) -> str:
        """Determine the type of interactive element"""
        if 'dropdown' in class_name.lower():
            return 'Button/Dropdown'
        elif 'filter' in class_name.lower() or 'filter' in text_content.lower():
            return 'Filter Button'
        elif 'sort' in class_name.lower() or 'sort' in text_content.lower():
            return 'Sort Button'
        elif 'toggle' in class_name.lower() or 'toggle' in text_content.lower():
            return 'Toggle Button'
        elif tag_name == 'a':
            return 'Link'
        elif tag_name == 'button':
            return 'Button'
        else:
            return 'Interactive Element'
    
    def _describe_visual_element(self, text_content: str, class_name: str, tag_name: str) -> str:
        """Create a description of the visual element"""
        if text_content:
            return f'"{text_content}" {tag_name}'
        elif class_name:
            return f'{tag_name} with class "{class_name}"'
        else:
            return f'{tag_name} element'
    
    def _describe_effect(self, requests: List[Dict], text_content: str) -> str:
        """Describe what the interaction does"""
        if not requests:
            return "No network requests triggered"
        
        # Analyze the requests to determine the effect
        request = requests[0]  # Use first request for simplicity
        
        if 'graphql' in request['url'].lower():
            return f"Executes GraphQL query"
        elif 'filter' in text_content.lower():
            return f"Filters content based on {text_content.lower()}"
        elif 'sort' in text_content.lower():
            return f"Sorts content by {text_content.lower()}"
        else:
            return f"Triggers request to {urlparse(request['url']).path}"
    
    def _describe_returns(self, requests: List[Dict]) -> str:
        """Describe what the request returns"""
        if not requests:
            return "No data returned"
        
        request = requests[0]
        
        if 'graphql' in request['url'].lower():
            return "JSON response with GraphQL data"
        elif request['url'].endswith('.json'):
            return "JSON data"
        else:
            return "HTML or other response data"
    
    def _generate_markdown(self, url: str) -> str:
        """Generate the final markdown documentation"""
        markdown = f"# Web Page Analysis: {url}\n\n"
        markdown += "## Static Content\n\n"
        markdown += "The page contains the following static HTML content:\n\n"
        markdown += f"```html\n{self.page_content[:1000]}...\n```\n\n"
        
        markdown += "## Interactive Elements\n\n"
        markdown += f"Found {len(self.interactive_elements)} interactive elements:\n\n"
        
        for element in self.interactive_elements:
            markdown += f"```{element.element_id}\n"
            markdown += f"type: {element.element_type}\n"
            markdown += f"visual_element: {element.visual_element}\n"
            markdown += f"trigger: {element.trigger}\n"
            
            if element.requests:
                request = element.requests[0]  # Use first request
                markdown += f"request: {request['method']} {request['url']}\n"
                
                # Extract arguments from request
                if request['post_data']:
                    try:
                        post_data = json.loads(request['post_data'])
                        markdown += f"arguments: {json.dumps(post_data, indent=2)}\n"
                    except:
                        markdown += f"arguments: {request['post_data']}\n"
                elif '?' in request['url']:
                    query_params = parse_qs(urlparse(request['url']).query)
                    markdown += f"arguments: {json.dumps(query_params, indent=2)}\n"
                else:
                    markdown += "arguments: {}\n"
            
            markdown += f"effect: {element.effect}\n"
            markdown += f"returns: {element.returns}\n"
            markdown += f"viewport_effect: {element.viewport_effect}\n"
            markdown += "```\n\n"
        
        return markdown


async def main():
    """Main function to run the analyzer"""
    from webportal.common import TEST_WEB_PAGE
    
    analyzer = WebPageAnalyzer()
    
    print(f"Analyzing webpage: {TEST_WEB_PAGE}")
    markdown_output = await analyzer.analyze_page(
        TEST_WEB_PAGE, 
        output_file="page_analysis.md"
    )
    
    print("Analysis complete! Output saved to page_analysis.md")
    print(f"Found {len(analyzer.interactive_elements)} interactive elements")


if __name__ == "__main__":
    asyncio.run(main())