import asyncio
import json
from playwright.async_api import async_playwright


async def debug_page_elements():
    """Debug what elements are actually available on the page"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set up request capture
        requests = []
        def capture_request(request):
            if any(pattern in request.url for pattern in ['graphql', 'api.github.com', 'hovercard', '/issues']):
                requests.append({
                    'method': request.method,
                    'url': request.url,
                    'post_data': request.post_data
                })
        
        page.on('request', capture_request)
        
        try:
            print("Navigating to GitHub issues page...")
            await page.goto("https://github.com/numpy/numpy/issues", wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            print(f"Initial requests captured: {len(requests)}")
            
            # Check what filter elements exist
            filter_elements = await page.query_selector_all('[data-menu-button], .js-issue-status-toggle, .js-sort-dropdown, button')
            print(f"Found {len(filter_elements)} potential filter elements")
            
            # Look for specific GitHub issue page elements
            selectors_to_test = [
                '.btn',
                'button',
                '[role="button"]',
                '.js-navigation-item',
                '.table-list-header button',
                '.subnav-search-context .btn',
                '.select-menu-button',
                '.states a',
                'details-menu',
                '.dropdown-toggle'
            ]
            
            for selector in selectors_to_test:
                elements = await page.query_selector_all(selector)
                visible_elements = []
                for el in elements:
                    if await el.is_visible():
                        text = await el.text_content()
                        visible_elements.append(text.strip()[:50] if text else "No text")
                
                if visible_elements:
                    print(f"Selector '{selector}': {len(visible_elements)} visible elements")
                    for i, text in enumerate(visible_elements[:3]):
                        print(f"  {i+1}. {text}")
            
            # Try clicking on some common elements
            common_clickables = [
                ('Open issues', 'a[href*="state=open"]'),
                ('Closed issues', 'a[href*="state=closed"]'),
                ('New issue', 'a[href*="/new"]'),
                ('Labels filter', 'button[data-hotkey="l"]'),
                ('Assignee filter', 'button[data-hotkey="a"]')
            ]
            
            initial_request_count = len(requests)
            
            for name, selector in common_clickables:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        print(f"Clicking on {name}...")
                        await element.click(timeout=3000)
                        await page.wait_for_timeout(1000)
                        
                        new_requests = requests[initial_request_count:]
                        if new_requests:
                            print(f"  Triggered {len(new_requests)} requests:")
                            for req in new_requests:
                                print(f"    {req['method']} {req['url']}")
                        else:
                            print(f"  No new requests triggered")
                        
                        initial_request_count = len(requests)
                except Exception as e:
                    print(f"  Failed to click {name}: {e}")
            
            # Look for issue hover cards
            print("\nTesting issue hover cards...")
            issue_links = await page.query_selector_all('a[data-hovercard-type="issue"]')
            print(f"Found {len(issue_links)} issue links")
            
            if issue_links:
                for i, link in enumerate(issue_links[:2]):
                    try:
                        print(f"Hovering over issue link {i+1}...")
                        await link.hover(timeout=3000)
                        await page.wait_for_timeout(1500)
                        
                        new_requests = requests[initial_request_count:]
                        if new_requests:
                            print(f"  Hover triggered {len(new_requests)} requests:")
                            for req in new_requests:
                                print(f"    {req['method']} {req['url']}")
                        
                        initial_request_count = len(requests)
                    except Exception as e:
                        print(f"  Failed to hover over issue {i+1}: {e}")
            
        finally:
            await browser.close()
        
        print(f"\nTotal requests captured: {len(requests)}")
        return requests


if __name__ == "__main__":
    asyncio.run(debug_page_elements())