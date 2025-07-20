import asyncio
from playwright.async_api import async_playwright

async def simple_test():
    """Simple test to verify Playwright is working"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set up request capturing
        requests = []
        
        def capture_request(request):
            if not any(ext in request.url for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.ico', '.woff']):
                requests.append({
                    'method': request.method,
                    'url': request.url
                })
        
        page.on('request', capture_request)
        
        # Navigate to test page
        print("Navigating to GitHub issues page...")
        await page.goto("https://github.com/numpy/numpy/issues", wait_until='networkidle')
        
        print(f"Captured {len(requests)} requests during page load")
        
        # Find some clickable elements
        buttons = await page.query_selector_all('button, .btn, [role="button"]')
        print(f"Found {len(buttons)} button-like elements")
        
        # Try clicking the first few visible buttons
        for i, button in enumerate(buttons[:3]):
            if await button.is_visible():
                initial_count = len(requests)
                try:
                    await button.click(timeout=3000)
                    await page.wait_for_timeout(1000)
                    new_requests = requests[initial_count:]
                    if new_requests:
                        text = await button.text_content()
                        print(f"Button '{text}' triggered {len(new_requests)} requests")
                        for req in new_requests:
                            print(f"  - {req['method']} {req['url']}")
                except Exception as e:
                    print(f"Failed to click button {i}: {e}")
        
        await browser.close()
        
        print("Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(simple_test())