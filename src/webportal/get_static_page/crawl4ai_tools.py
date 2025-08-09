import asyncio
import random
import os

from crawl4ai import AsyncWebCrawler


async def parse_web_page_using_crawl4ai(url: str):
    # Stealth configuration
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    stealth_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate", 
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
    
    browser_args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-features=VizDisplayCompositor",
        "--disable-ipc-flooding-protection",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-extensions",
        "--disable-plugins",
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ]
    
    # Optional proxy support
    proxy_server = None
    if os.getenv("USE_PROXY", "false").lower() == "true":
        try:
            from webportal.stealth.proxy_manager import get_proxy_manager
            proxy_manager = get_proxy_manager()
            proxy_dict = proxy_manager.get_random_proxy()
            if proxy_dict:
                proxy_server = proxy_dict['http']
        except Exception as e:
            print(f"Proxy setup failed: {e}")
    
    async with AsyncWebCrawler(
        browser_config={
            "user_agent": random.choice(user_agents),
            "headers": stealth_headers,
            "args": browser_args,
            "proxy": proxy_server
        },
        verbose=False
    ) as crawler:
        # Add random delay before crawling
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        result = await crawler.arun(
            url=url,
            js_code="""
            // Mask automation signatures
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            delete navigator.__proto__.webdriver;
            """
        )
        return result.markdown


def get_markdown_using_crawl4ai(url: str):
    return asyncio.run(parse_web_page_using_crawl4ai(url))
