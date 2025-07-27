#!/usr/bin/env python3
"""Test script to verify Selenium Grid works with multiprocessing"""

import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def test_grid_session(process_id: int) -> str:
    """Test function that creates a Grid session"""
    grid_url = "http://localhost:4444/wd/hub"
    
    # Basic Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Remote(
        command_executor=grid_url,
        options=chrome_options
    )
    
    # Test basic functionality
    driver.get("https://www.google.com")
    title = driver.title
    session_id = driver.session_id
    
    driver.quit()
    
    return f"Process {process_id}: Session {session_id}, Title: {title}"


def main():
    """Test multiprocessing with Selenium Grid"""
    print("Testing Selenium Grid with multiprocessing...")
    
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(test_grid_session, i) for i in range(5)]
        
        for future in futures:
            result = future.result()
            print(result)
    
    print("✅ All processes completed successfully!")


if __name__ == "__main__":
    main()