"""
Command-line interface for WebPortal.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional

from .network_crawler import crawl_with_network
from .web_crawler import crawl_website


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="WebPortal - Extract static content and dynamic elements from webpages"
    )
    parser.add_argument("url", help="URL to crawl")
    parser.add_argument(
        "-o", "--output", 
        help="Output file for markdown summary (default: auto-generated filename)"
    )
    parser.add_argument(
        "--headless", 
        action="store_true", 
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    parser.add_argument(
        "--no-headless", 
        action="store_true",
        help="Run browser in visible mode"
    )
    parser.add_argument(
        "--network", 
        action="store_true",
        help="Use network-aware crawler to capture API endpoints"
    )
    parser.add_argument(
        "--wait-time", 
        type=int, 
        default=3000,
        help="Time to wait for dynamic content to load in milliseconds (default: 3000)"
    )
    
    args = parser.parse_args()
    
    # Handle headless mode
    headless = args.headless and not args.no_headless
    
    # Generate output filename if not provided
    output_file = args.output
    if not output_file:
        from urllib.parse import urlparse
        parsed_url = urlparse(args.url)
        domain = parsed_url.netloc.replace(".", "_")
        path = parsed_url.path.replace("/", "_").replace(".", "_")
        if not path:
            path = "home"
        output_file = f"crawl_{domain}{path}.md"
    
    try:
        print(f"Crawling {args.url}...")
        print(f"Output will be saved to: {output_file}")
        
        if args.network:
            print("Using network-aware crawler...")
            data = await crawl_with_network(
                url=args.url,
                output_file=output_file,
                headless=headless
            )
            print(f"Found {len(data.dynamic_elements)} dynamic elements")
            print(f"Captured {len(data.network_requests)} network requests")
            print(f"Discovered {len(data.api_endpoints)} API endpoints")
        else:
            print("Using basic crawler...")
            data = await crawl_website(
                url=args.url,
                output_file=output_file,
                headless=headless
            )
            print(f"Found {len(data.dynamic_elements)} dynamic elements")
        
        print(f"\n✅ Crawling completed! Check {output_file} for the markdown summary.")
        
    except Exception as e:
        print(f"❌ Error during crawling: {e}", file=sys.stderr)
        sys.exit(1)


def run_cli():
    """Entry point for CLI."""
    asyncio.run(main())


if __name__ == "__main__":
    run_cli() 