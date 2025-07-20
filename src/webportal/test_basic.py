"""
Basic test script for WebPortal package.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from webportal import crawl_website


async def test_basic_crawler():
    """Test the basic web crawler."""
    print("Testing basic web crawler...")
    
    try:
        # Use a simple test page
        url = "https://httpbin.org/html"
        data = await crawl_website(url)
        
        print(f"✅ Successfully crawled {url}")
        print(f"   Title: {data.title}")
        print(f"   Static content length: {len(data.static_content)}")
        print(f"   Dynamic elements: {len(data.dynamic_elements)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run the test."""
    print("Running WebPortal basic test...")
    
    success = await test_basic_crawler()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 