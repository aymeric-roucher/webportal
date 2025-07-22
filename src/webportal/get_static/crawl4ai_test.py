import asyncio
from crawl4ai import AsyncWebCrawler
from webportal.common import TEST_WEB_PAGE


async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=TEST_WEB_PAGE,
        )
        print(result.markdown)  # Show the first 300 characters of extracted text

    with open("crawl4ai_test.md", "w") as f:
        f.write(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())
