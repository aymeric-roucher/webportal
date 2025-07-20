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


class EnhancedWebPageAnalyzer:
    """Enhanced analyzer focused on GitHub-like pages"""
    
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
            
            # Set up request/response intercepting with filtering
            page.on('request', self._capture_filtered_request)
            
            try:
                # Navigate to the page
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Get static content (first 2000 chars for brevity)
                full_content = await page.content()
                self.page_content = full_content[:2000] + "..." if len(full_content) > 2000 else full_content
                
                # Focus on GitHub-specific interactive elements
                await self._discover_github_elements(page)
                
                # Generate markdown
                markdown_content = self._generate_markdown(url)
                
                if output_file:
                    Path(output_file).write_text(markdown_content)
                    
                return markdown_content
                
            finally:
                await browser.close()
    
    async def _discover_github_elements(self, page: Page):
        """Discover GitHub-specific interactive elements"""
        
        # GitHub-specific selectors for issues pages
        github_selectors = {
            'filter_author': 'button[data-menu-button=""]',
            'filter_label': 'details-menu[data-menu-button=""]',
            'filter_sort': 'details-menu .js-menu-container',
            'issue_links': 'a[data-hovercard-type="issue"]',
            'state_buttons': '.table-list-header button',
            'search_input': '.subnav-search input',
            'new_issue_button': 'a[data-hotkey="c"]',
            'milestone_filter': 'details-menu[data-target="milestones-filter.container"]',
            'assignee_filter': 'details-menu[data-target="assignees-filter.container"]'
        }
        
        for element_name, selector in github_selectors.items():
            await self._analyze_github_element(page, selector, element_name)
    
    async def _analyze_github_element(self, page: Page, selector: str, element_name: str):
        """Analyze a specific GitHub element"""
        try:
            elements = await page.query_selector_all(selector)
            
            for i, element in enumerate(elements[:3]):  # Limit to 3 per type
                if not await element.is_visible():
                    continue
                
                initial_request_count = len(self.captured_requests)
                
                # Get element info
                text_content = await element.evaluate('el => el.textContent?.trim() || ""')
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                
                # Try different interactions
                interactions = ['click', 'hover'] if 'hover' in element_name else ['click']
                
                for interaction in interactions:
                    try:
                        if interaction == 'click':
                            await element.click(timeout=3000)
                        elif interaction == 'hover':
                            await element.hover(timeout=3000)
                        
                        # Wait for requests
                        await page.wait_for_timeout(1500)
                        
                        # Check for new requests
                        new_requests = self.captured_requests[initial_request_count:]
                        
                        if new_requests:
                            element_id = f"interactive_element_{element_name}_{i}"
                            
                            # Create detailed description based on element type
                            element_type, visual_desc, effect_desc = self._get_github_element_details(
                                element_name, text_content, new_requests
                            )
                            
                            interactive_el = InteractiveElement(
                                element_id=element_id,
                                element_type=element_type,
                                visual_element=visual_desc,
                                trigger=interaction.capitalize(),
                                selector=selector,
                                requests=new_requests,
                                effect=effect_desc,
                                returns=self._analyze_response_type(new_requests),
                                viewport_effect=self._determine_viewport_effect(element_name)
                            )
                            
                            self.interactive_elements.append(interactive_el)
                            initial_request_count = len(self.captured_requests)
                            break  # Only one successful interaction per element
                            
                    except Exception:
                        continue
                        
        except Exception:
            pass
    
    def _capture_filtered_request(self, request: Request):
        """Capture only relevant requests"""
        url = request.url
        
        # Filter out common resources and analytics (but keep GraphQL and API calls)
        if any(ext in url for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.ico', '.woff', '.svg']):
            return
        
        # Focus on GitHub API calls and important requests
        if any(pattern in url for pattern in [
            'graphql', 'api.github.com', 'hovercard', 'search', 'filter', 
            '/issues', '_graphql', 'suggest', 'auto_complete'
        ]) or request.method == 'POST':
            
            request_data = {
                'method': request.method,
                'url': url,
                'headers': dict(request.headers),
                'post_data': request.post_data
            }
            self.captured_requests.append(request_data)
    
    def _get_github_element_details(self, element_name: str, text_content: str, requests: List[Dict]) -> tuple:
        """Get GitHub-specific element details"""
        
        element_type = "Button/Dropdown"
        visual_desc = f'"{text_content}" button in the issues filter bar'
        effect_desc = f"Loads {element_name} options for filtering"
        
        if 'author' in element_name:
            element_type = "Button/Dropdown"
            visual_desc = '"Author" button on top of the issues list, in the filter bar'
            effect_desc = "Loads author suggestions for filtering"
        elif 'label' in element_name:
            element_type = "Button/Dropdown"
            visual_desc = '"Labels" button on top of the issues list, in the filter bar'
            effect_desc = "Loads all available labels for filtering issues"
        elif 'sort' in element_name:
            element_type = "Button/Dropdown"
            visual_desc = f'Sort dropdown with "{text_content}" option'
            effect_desc = f"Sorts issues by {text_content.lower()}"
        elif 'state' in element_name:
            element_type = "Button/Toggle"
            visual_desc = f'"{text_content}" button in the issues filter bar'
            effect_desc = f"Filters issues to show {text_content.lower()} issues"
        elif 'hover' in element_name:
            element_type = "Hover trigger"
            visual_desc = "Issue links"
            effect_desc = "Displays a popup card to view issue details"
        elif 'issue_links' in element_name:
            element_type = "Link"
            visual_desc = f"Issue link: {text_content}"
            effect_desc = "Navigates to issue details page"
        
        return element_type, visual_desc, effect_desc
    
    def _analyze_response_type(self, requests: List[Dict]) -> str:
        """Analyze what type of response is expected"""
        if not requests:
            return "No data returned"
        
        request = requests[0]
        url = request['url']
        
        if 'graphql' in url.lower():
            return "JSON response with GraphQL data"
        elif 'hovercard' in url:
            return "HTML with issue title, description preview, and labels"
        elif 'search' in url or 'filter' in url:
            return "JSON with filtered results"
        elif request['method'] == 'GET' and '/issues' in url:
            return "HTML page with filtered list of issues"
        else:
            return "JSON or HTML response data"
    
    def _determine_viewport_effect(self, element_name: str) -> str:
        """Determine viewport effects"""
        if 'hover' in element_name:
            return "none"
        elif 'state' in element_name or 'sort' in element_name:
            return "Reloads the issues list with filtered/sorted results"
        elif 'filter' in element_name:
            return "Opens dropdown showing filter options"
        else:
            return "May update page content or open dropdown"
    
    def _generate_markdown(self, url: str) -> str:
        """Generate enhanced markdown documentation"""
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
                
                # Format arguments nicely
                if request['post_data']:
                    try:
                        post_data = json.loads(request['post_data'])
                        formatted_args = json.dumps(post_data, indent=2)
                    except:
                        formatted_args = str(request['post_data'])
                    markdown += f"arguments: {{\n{formatted_args}\n}}\n"
                elif '?' in request['url']:
                    parsed_url = urlparse(request['url'])
                    query_params = parse_qs(parsed_url.query)
                    formatted_args = json.dumps(query_params, indent=2)
                    markdown += f"arguments: {{\n{formatted_args}\n}}\n"
                else:
                    markdown += "arguments: {}\n"
            
            markdown += f"effect: {element.effect}\n"
            markdown += f"returns: {element.returns}\n"
            markdown += f"viewport_effect: {element.viewport_effect}\n"
            markdown += "```\n\n"
        
        return markdown


async def main():
    """Main function to run the enhanced analyzer"""
    from webportal.common import TEST_WEB_PAGE
    
    analyzer = EnhancedWebPageAnalyzer()
    
    print(f"Analyzing webpage: {TEST_WEB_PAGE}")
    markdown_output = await analyzer.analyze_page(
        TEST_WEB_PAGE, 
        output_file="enhanced_page_analysis.md"
    )
    
    print("Enhanced analysis complete! Output saved to enhanced_page_analysis.md")
    print(f"Found {len(analyzer.interactive_elements)} interactive elements")


if __name__ == "__main__":
    asyncio.run(main())