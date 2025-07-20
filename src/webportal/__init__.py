"""
WebPortal - A Python package for extracting static content and dynamic elements from webpages.
"""

from .web_crawler import WebCrawler, WebPageData, crawl_website
from .network_crawler import NetworkAwareCrawler, EnhancedWebPageData, crawl_with_network

__version__ = "0.1.0"
__all__ = [
    "WebCrawler",
    "WebPageData", 
    "crawl_website",
    "NetworkAwareCrawler",
    "EnhancedWebPageData",
    "crawl_with_network"
]
