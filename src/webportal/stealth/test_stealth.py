#!/usr/bin/env python3

import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from playwright.async_api import async_playwright
import requests


def test_selenium_stealth():
    """Test Selenium with stealth configuration"""
    print("Testing Selenium stealth configuration...")
    
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    # Execute stealth JavaScript
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            delete navigator.__proto__.webdriver;
        '''
    })
    
    # Test bot detection sites
    test_sites = [
        "https://bot.sannysoft.com/",
        "https://arh.antoinevastel.com/bots/areyouheadless",
        "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
    ]
    
    for site in test_sites:
        print(f"Testing: {site}")
        try:
            driver.get(site)
            page_title = driver.title
            print(f"✓ Successfully loaded: {page_title}")
            
            # Check for common bot detection indicators
            webdriver_detected = driver.execute_script("return navigator.webdriver")
            print(f"webdriver property: {webdriver_detected}")
            
            user_agent = driver.execute_script("return navigator.userAgent")
            print(f"User agent: {user_agent}")
            
        except Exception as e:
            print(f"✗ Failed to load {site}: {e}")
    
    driver.quit()


async def test_playwright_stealth():
    """Test Playwright with stealth configuration"""
    print("\nTesting Playwright stealth configuration...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9"
            }
        )
        
        page = await context.new_page()
        
        # Add stealth scripts
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            delete navigator.__proto__.webdriver;
        """)
        
        test_sites = [
            "https://httpbin.org/headers", 
            "https://httpbin.org/user-agent"
        ]
        
        for site in test_sites:
            print(f"Testing: {site}")
            try:
                await page.goto(site)
                title = await page.title()
                print(f"✓ Successfully loaded: {title}")
                
                # Check webdriver property
                webdriver_detected = await page.evaluate("navigator.webdriver")
                print(f"webdriver property: {webdriver_detected}")
                
            except Exception as e:
                print(f"✗ Failed to load {site}: {e}")
        
        await browser.close()


def test_requests_headers():
    """Test request headers for stealth"""
    print("\nTesting requests with stealth headers...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none"
    }
    
    try:
        response = requests.get("https://httpbin.org/headers", headers=headers, timeout=10)
        print(f"✓ Request successful: {response.status_code}")
        data = response.json()
        print(f"Headers sent: {data['headers'].get('User-Agent', 'None')}")
    except Exception as e:
        print(f"✗ Request failed: {e}")


def test_proxy_manager():
    """Test proxy manager functionality"""
    print("\nTesting proxy manager...")
    
    try:
        from webportal.stealth.proxy_manager import get_proxy_manager
        
        proxy_manager = get_proxy_manager()
        proxy_dict = proxy_manager.get_random_proxy()
        
        if proxy_dict:
            print(f"✓ Proxy obtained: {proxy_dict}")
            
            # Test proxy with simple request
            try:
                response = requests.get("https://httpbin.org/ip", proxies=proxy_dict, timeout=10)
                if response.status_code == 200:
                    print(f"✓ Proxy works: {response.json()}")
                else:
                    print(f"✗ Proxy failed with status: {response.status_code}")
            except Exception as e:
                print(f"✗ Proxy test failed: {e}")
        else:
            print("✗ No proxy available")
            
    except Exception as e:
        print(f"✗ Proxy manager error: {e}")


async def main():
    """Run all stealth tests"""
    print("=" * 60)
    print("STEALTH CRAWLING CONFIGURATION TEST")
    print("=" * 60)
    
    # Test Selenium stealth
    test_selenium_stealth()
    
    # Test Playwright stealth  
    await test_playwright_stealth()
    
    # Test request headers
    test_requests_headers()
    
    # Test proxy manager (optional)
    test_proxy_manager()
    
    print("\n" + "=" * 60)
    print("STEALTH TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())