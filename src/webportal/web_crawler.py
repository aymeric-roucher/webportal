"""
Web crawler module using Playwright to extract static content and dynamic elements.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re

from playwright.async_api import async_playwright, Page, ElementHandle
from bs4 import BeautifulSoup
import markdown


@dataclass
class DynamicElement:
    """Represents a dynamic element found on the page."""
    type: str  # button, form, link, input, etc.
    selector: str
    text: str
    attributes: Dict[str, str]
    action: str  # click, submit, input, etc.
    url: Optional[str] = None
    method: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class WebPageData:
    """Container for extracted webpage data."""
    url: str
    title: str
    static_content: str
    dynamic_elements: List[DynamicElement]
    api_endpoints: List[Dict[str, Any]]
    markdown_summary: str


class WebCrawler:
    """Main web crawler class using Playwright."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def crawl_page(self, url: str, wait_time: int = 3000) -> WebPageData:
        """
        Crawl a webpage and extract both static and dynamic content.
        
        Args:
            url: The URL to crawl
            wait_time: Time to wait for dynamic content to load (ms)
            
        Returns:
            WebPageData containing all extracted information
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
        
        # Extract API endpoints from network requests
        api_endpoints = await self._extract_api_endpoints()
        
        # Generate markdown summary
        markdown_summary = self._generate_markdown_summary(
            url, title, static_content, dynamic_elements, api_endpoints
        )
        
        return WebPageData(
            url=url,
            title=title,
            static_content=static_content,
            dynamic_elements=dynamic_elements,
            api_endpoints=api_endpoints,
            markdown_summary=markdown_summary
        )
    
    async def _extract_static_content(self) -> str:
        """Extract static content from the page."""
        # Get the main content area
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
    
    async def _extract_dynamic_elements(self) -> List[DynamicElement]:
        """Extract dynamic elements like buttons, forms, links, etc."""
        elements = []
        
        # Extract buttons
        buttons = await self.page.query_selector_all("button, input[type='button'], input[type='submit']")
        for button in buttons:
            element = await self._analyze_button(button)
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
            element = await self._analyze_link(link)
            if element:
                elements.append(element)
        
        # Extract inputs
        inputs = await self.page.query_selector_all("input:not([type='button']):not([type='submit'])")
        for input_elem in inputs:
            element = await self._analyze_input(input_elem)
            if element:
                elements.append(element)
        
        return elements
    
    async def _analyze_button(self, button: ElementHandle) -> Optional[DynamicElement]:
        """Analyze a button element."""
        try:
            text = await button.inner_text()
            if not text.strip():
                text = await button.get_attribute("value") or await button.get_attribute("aria-label") or "Button"
            
            selector = await self._generate_selector(button)
            attributes = await self._get_attributes(button)
            
            return DynamicElement(
                type="button",
                selector=selector,
                text=text.strip(),
                attributes=attributes,
                action="click"
            )
        except Exception:
            return None
    
    async def _analyze_form(self, form: ElementHandle) -> List[DynamicElement]:
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
            
            elements.append(DynamicElement(
                type="form",
                selector=selector,
                text="Form",
                attributes=attributes,
                action="submit",
                url=action,
                method=method,
                data=form_data
            ))
            
        except Exception:
            pass
        
        return elements
    
    async def _analyze_link(self, link: ElementHandle) -> Optional[DynamicElement]:
        """Analyze a link element."""
        try:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            
            if not text.strip():
                return None
            
            selector = await self._generate_selector(link)
            attributes = await self._get_attributes(link)
            
            return DynamicElement(
                type="link",
                selector=selector,
                text=text.strip(),
                attributes=attributes,
                action="click",
                url=href
            )
        except Exception:
            return None
    
    async def _analyze_input(self, input_elem: ElementHandle) -> Optional[DynamicElement]:
        """Analyze an input element."""
        try:
            input_type = await input_elem.get_attribute("type") or "text"
            name = await input_elem.get_attribute("name")
            placeholder = await input_elem.get_attribute("placeholder")
            
            if not name:
                return None
            
            selector = await self._generate_selector(input_elem)
            attributes = await self._get_attributes(input_elem)
            
            return DynamicElement(
                type="input",
                selector=selector,
                text=placeholder or name,
                attributes=attributes,
                action="input",
                data={name: {"type": input_type, "placeholder": placeholder}}
            )
        except Exception:
            return None
    
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
    
    async def _extract_api_endpoints(self) -> List[Dict[str, Any]]:
        """Extract API endpoints from network requests."""
        # This would require intercepting network requests
        # For now, return empty list - can be enhanced later
        return []
    
    def _generate_markdown_summary(
        self, 
        url: str, 
        title: str, 
        static_content: str, 
        dynamic_elements: List[DynamicElement],
        api_endpoints: List[Dict[str, Any]]
    ) -> str:
        """Generate a markdown summary for AI agents."""
        markdown_parts = []
        
        # Page header
        markdown_parts.append(f"# {title}")
        markdown_parts.append(f"**URL:** {url}\n")
        
        # Static content summary
        markdown_parts.append("## Static Content")
        content_preview = static_content[:500] + "..." if len(static_content) > 500 else static_content
        markdown_parts.append(content_preview + "\n")
        
        # Dynamic elements
        if dynamic_elements:
            markdown_parts.append("## Interactive Elements")
            
            # Group by type
            by_type = {}
            for elem in dynamic_elements:
                if elem.type not in by_type:
                    by_type[elem.type] = []
                by_type[elem.type].append(elem)
            
            for elem_type, elements in by_type.items():
                markdown_parts.append(f"### {elem_type.title()}s")
                for elem in elements:
                    markdown_parts.append(f"- **{elem.text}**")
                    markdown_parts.append(f"  - Action: {elem.action}")
                    markdown_parts.append(f"  - Selector: `{elem.selector}`")
                    if elem.url:
                        markdown_parts.append(f"  - URL: {elem.url}")
                    if elem.method:
                        markdown_parts.append(f"  - Method: {elem.method}")
                    if elem.data:
                        markdown_parts.append(f"  - Data: {json.dumps(elem.data, indent=2)}")
                    markdown_parts.append("")
        
        # API endpoints
        if api_endpoints:
            markdown_parts.append("## API Endpoints")
            for endpoint in api_endpoints:
                markdown_parts.append(f"- {endpoint.get('method', 'GET')} {endpoint.get('url', '')}")
        
        return "\n".join(markdown_parts)


async def crawl_website(url: str, output_file: str = None, headless: bool = True) -> WebPageData:
    """
    Convenience function to crawl a website and optionally save to file.
    
    Args:
        url: The URL to crawl
        output_file: Optional file path to save the markdown summary
        headless: Whether to run browser in headless mode
        
    Returns:
        WebPageData containing all extracted information
    """
    async with WebCrawler(headless=headless) as crawler:
        data = await crawler.crawl_page(url)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data.markdown_summary)
        
        return data 