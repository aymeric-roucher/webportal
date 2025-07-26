import asyncio

from crawl4ai import AsyncWebCrawler


async def parse_web_page_using_crawl4ai(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        return result.markdown  # Show the first 300 characters of extracted text


def get_markdown_using_crawl4ai(url: str):
    return asyncio.run(parse_web_page_using_crawl4ai(url))
