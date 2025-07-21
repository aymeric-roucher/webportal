import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright, Page, Request
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


class FinalWebPageAnalyzer:
    """Final comprehensive web page analyzer"""
    
    def __init__(self):
        self.captured_requests: List[Dict[str, Any]] = []
        self.page_content: str = ""
        self.interactive_elements: List[InteractiveElement] = []
        
    async def analyze_page(self, url: str, output_file: Optional[str] = None) -> str:
        """Analyze a webpage and generate markdown documentation"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Set up request/response intercepting
            page.on('request', self._capture_relevant_request)
            
            try:
                print(f"Navigating to {url}...")
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(3000)  # Wait for dynamic content
                
                # Get static content
                full_content = await page.content()
                self.page_content = full_content[:2000] + "..." if len(full_content) > 2000 else full_content
                
                print("Discovering interactive elements...")
                await self._discover_all_elements(page)
                
                # Generate markdown
                markdown_content = self._generate_markdown(url)
                
                if output_file:
                    Path(output_file).write_text(markdown_content)
                    print(f"Analysis saved to {output_file}")
                    
                return markdown_content
                
            finally:
                await browser.close()
    
    async def _discover_all_elements(self, page: Page):
        """Discover all interactive elements using a comprehensive approach"""
        
        # Broad selector strategy - find all potentially interactive elements
        broad_selectors = [
            'button',
            'a[href]',
            'input[type="button"]',
            'input[type="submit"]',
            '[role="button"]',
            '[onclick]',
            '.btn',
            '.button',
            'select',
            '[tabindex="0"]',
            '[data-action]',
            '[data-hotkey]',
            'details',
            'summary'
        ]
        
        all_elements = []
        
        # Collect all potentially interactive elements
        for selector in broad_selectors:
            elements = await page.query_selector_all(selector)
            for element in elements:
                if await element.is_visible():
                    all_elements.append((element, selector))
        
        print(f"Found {len(all_elements)} potentially interactive elements")
        
        # Analyze each element (limit to prevent overwhelming output)
        for i, (element, selector) in enumerate(all_elements[:20]):  # Limit to first 20
            await self._analyze_element_comprehensive(page, element, selector, i)
    
    async def _analyze_element_comprehensive(self, page: Page, element, selector: str, index: int):
        """Comprehensively analyze an element"""
        try:
            # Get element details
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            text_content = await element.evaluate('el => el.textContent?.trim() || ""')
            class_name = await element.evaluate('el => el.className || ""')
            href = await element.evaluate('el => el.href || ""')
            data_attrs = await element.evaluate('''el => {
                const attrs = {};
                for (let attr of el.attributes) {
                    if (attr.name.startsWith('data-')) {
                        attrs[attr.name] = attr.value;
                    }
                }
                return attrs;
            }''')
            
            # Skip if no meaningful content
            if not text_content and not class_name and not href:
                return
                
            print(f"Analyzing element {index + 1}: {tag_name} - {text_content[:30]}")
            
            initial_request_count = len(self.captured_requests)
            
            # Try different interactions
            interactions_to_try = ['click']
            if 'hover' in str(data_attrs) or 'hovercard' in str(data_attrs):
                interactions_to_try.append('hover')
            
            for interaction_type in interactions_to_try:
                try:
                    print(f"  Trying {interaction_type}...")
                    
                    if interaction_type == 'click':
                        await element.click(timeout=5000)
                    elif interaction_type == 'hover':
                        await element.hover(timeout=5000)
                    
                    # Wait for potential network requests
                    await page.wait_for_timeout(2000)
                    
                    # Check if new requests were captured
                    new_requests = self.captured_requests[initial_request_count:]
                    
                    if new_requests:
                        print(f"    Success! Captured {len(new_requests)} requests")
                        
                        # Create interactive element
                        element_id = f"interactive_element_{index}_{interaction_type}"
                        
                        element_type = self._determine_element_type(tag_name, class_name, text_content, data_attrs)
                        visual_element = self._describe_visual_element(text_content, class_name, tag_name, href)
                        effect = self._describe_effect(new_requests, text_content, interaction_type)
                        returns = self._describe_returns(new_requests)
                        viewport_effect = self._determine_viewport_effect(new_requests, interaction_type)
                        
                        interactive_el = InteractiveElement(
                            element_id=element_id,
                            element_type=element_type,
                            visual_element=visual_element,
                            trigger=interaction_type.capitalize(),
                            selector=selector,
                            requests=new_requests,
                            effect=effect,
                            returns=returns,
                            viewport_effect=viewport_effect
                        )
                        
                        self.interactive_elements.append(interactive_el)
                        initial_request_count = len(self.captured_requests)
                        break  # One successful interaction per element
                    else:
                        print(f"    No requests captured for {interaction_type}")
                        
                except Exception as e:
                    print(f"    Failed {interaction_type}: {str(e)[:50]}")
                    continue
                    
        except Exception as e:
            print(f"  Error analyzing element: {str(e)[:50]}")
    
    def _capture_relevant_request(self, request: Request):
        """Capture relevant requests (filter out resources)"""
        url = request.url
        
        # Filter out static resources
        if any(ext in url for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.ico', '.woff', '.svg', '.ttf']):
            return
        
        # Capture interesting requests
        if (request.method == 'POST' or 
            any(pattern in url for pattern in [
                'graphql', 'api', 'hovercard', 'search', 'filter', 
                'issues', 'suggest', 'autocomplete', '_graphql'
            ])):
            
            request_data = {
                'method': request.method,
                'url': url,
                'headers': {k: v for k, v in request.headers.items() if k.lower() in ['content-type', 'accept']},
                'post_data': request.post_data
            }
            self.captured_requests.append(request_data)
    
    def _determine_element_type(self, tag_name: str, class_name: str, text_content: str, data_attrs: dict) -> str:
        """Determine the type of interactive element"""
        if 'dropdown' in class_name.lower() or 'menu' in class_name.lower():
            return 'Button/Dropdown'
        elif 'filter' in class_name.lower() or 'filter' in text_content.lower():
            return 'Filter Button'
        elif 'sort' in class_name.lower() or 'sort' in text_content.lower():
            return 'Sort Button'
        elif 'toggle' in class_name.lower():
            return 'Toggle Button'
        elif 'hovercard' in str(data_attrs):
            return 'Hover trigger'
        elif tag_name == 'a':
            return 'Link'
        elif tag_name == 'button':
            return 'Button'
        elif tag_name == 'input':
            return 'Input'
        elif tag_name == 'select':
            return 'Dropdown'
        else:
            return 'Interactive Element'
    
    def _describe_visual_element(self, text_content: str, class_name: str, tag_name: str, href: str) -> str:
        """Create a description of the visual element"""
        if text_content.strip():
            return f'"{text_content.strip()}" {tag_name}'
        elif href:
            return f'{tag_name} with href "{href}"'
        elif class_name:
            return f'{tag_name} with class "{class_name}"'
        else:
            return f'{tag_name} element'
    
    def _describe_effect(self, requests: List[Dict], text_content: str, interaction_type: str) -> str:
        """Describe what the interaction does"""
        if not requests:
            return "No network requests triggered"
        
        request = requests[0]
        url = request['url']
        
        if 'graphql' in url.lower():
            return "Executes GraphQL query"
        elif 'hovercard' in url:
            return "Displays a popup card with additional information"
        elif 'filter' in text_content.lower():
            return f"Filters content based on {text_content.lower()}"
        elif 'sort' in text_content.lower():
            return f"Sorts content by {text_content.lower()}"
        elif interaction_type == 'hover':
            return "Shows additional information on hover"
        elif request['method'] == 'POST':
            return f"Submits data to {urlparse(url).path}"
        else:
            return f"Loads data from {urlparse(url).path}"
    
    def _describe_returns(self, requests: List[Dict]) -> str:
        """Describe what the request returns"""
        if not requests:
            return "No data returned"
        
        request = requests[0]
        url = request['url']
        
        if 'graphql' in url.lower():
            return "JSON response with GraphQL data"
        elif 'hovercard' in url:
            return "HTML with hover card content"
        elif request['method'] == 'POST':
            return "Response data from server"
        elif '.json' in url:
            return "JSON data"
        else:
            return "HTML or other response data"
    
    def _determine_viewport_effect(self, requests: List[Dict], interaction_type: str) -> str:
        """Determine viewport effects"""
        if interaction_type == 'hover':
            return "Shows popup or tooltip"
        elif any('filter' in req['url'] or 'sort' in req['url'] for req in requests):
            return "Updates page content with filtered/sorted results"
        elif requests and requests[0]['method'] == 'GET':
            return "May navigate to new page or update current page"
        else:
            return "May update page content"
    
    def _generate_markdown(self, url: str) -> str:
        """Generate the final markdown documentation"""
        markdown = f"# Web Page Analysis: {url}\n\n"
        markdown += "## Static Content\n\n"
        markdown += "The page contains the following static HTML content:\n\n"
        markdown += f"```html\n{self.page_content}\n```\n\n"
        
        markdown += "## Interactive Elements\n\n"
        markdown += f"Found {len(self.interactive_elements)} interactive elements:\n\n"
        
        for element in self.interactive_elements:
            markdown += f"```{element.element_id}\n"
            markdown += f"type: {element.element_type}\n"
            markdown += f"visual_element: {element.visual_element}\n"
            markdown += f"trigger: {element.trigger}\n"
            
            if element.requests:
                request = element.requests[0]
                markdown += f"request: {request['method']} {request['url']}\n"
                
                # Format arguments
                args_dict = {}
                if request['post_data']:
                    try:
                        args_dict = json.loads(request['post_data'])
                    except:
                        args_dict = {"post_data": request['post_data']}
                elif '?' in request['url']:
                    parsed_url = urlparse(request['url'])
                    args_dict = parse_qs(parsed_url.query)
                
                if args_dict:
                    markdown += "arguments: {\n"
                    for key, value in args_dict.items():
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        markdown += f'  "{key}": {json.dumps(value)},\n'
                    markdown += "}\n"
                else:
                    markdown += "arguments: {}\n"
            
            markdown += f"effect: {element.effect}\n"
            markdown += f"returns: {element.returns}\n"
            markdown += f"viewport_effect: {element.viewport_effect}\n"
            markdown += "```\n\n"
        
        return markdown


async def main():
    """Main function to run the final analyzer"""
    from webportal.common import TEST_WEB_PAGE
    
    analyzer = FinalWebPageAnalyzer()
    
    print(f"Starting comprehensive analysis of: {TEST_WEB_PAGE}")
    markdown_output = await analyzer.analyze_page(
        TEST_WEB_PAGE, 
        output_file="final_page_analysis.md"
    )
    
    print(f"\nAnalysis complete!")
    print(f"Found {len(analyzer.interactive_elements)} interactive elements")
    print(f"Captured {len(analyzer.captured_requests)} requests")
    print("Output saved to final_page_analysis.md")


if __name__ == "__main__":
    asyncio.run(main())