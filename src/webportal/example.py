"""
Example usage of WebPortal package.
"""

import asyncio
from webportal.network_crawler import crawl_with_network
from webportal.web_crawler import crawl_website


async def basic_example():
    """Basic example using the simple crawler."""
    print("=== Basic Crawler Example ===")
    
    url = "https://httpbin.org/forms/post"
    print(f"Crawling {url}...")
    
    data = await crawl_website(url, output_file="basic_example.md")
    
    print(f"Title: {data.title}")
    print(f"Static content length: {len(data.static_content)} characters")
    print(f"Dynamic elements found: {len(data.dynamic_elements)}")
    
    # Show some dynamic elements
    for elem in data.dynamic_elements[:3]:
        print(f"- {elem.type}: {elem.text}")


async def network_example():
    """Example using the network-aware crawler."""
    print("\n=== Network-Aware Crawler Example ===")
    
    url = "https://httpbin.org/forms/post"
    print(f"Crawling {url} with network interception...")
    
    data = await crawl_with_network(url, output_file="network_example.md")
    
    print(f"Title: {data.title}")
    print(f"Static content length: {len(data.static_content)} characters")
    print(f"Dynamic elements found: {len(data.dynamic_elements)}")
    print(f"Network requests captured: {len(data.network_requests)}")
    print(f"API endpoints discovered: {len(data.api_endpoints)}")
    
    # Show interaction tools
    print(f"Interaction tools generated: {len(data.interaction_tools)}")
    for tool in data.interaction_tools[:3]:
        print(f"- {tool['name']}: {tool['description']}")


async def main():
    """Run all examples."""
    try:
        await basic_example()
        await network_example()
        print("\n✅ Examples completed! Check the generated .md files.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 