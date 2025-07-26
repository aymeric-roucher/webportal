import asyncio
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from tqdm import tqdm

from webportal.get_interactive.convert_to_api_docs import (
    create_api_docs_conversion_prompt,
)
from webportal.get_interactive.main import ingest_from_prompt
from webportal.inference import call_llm
from webportal.map_website.crawl import crawl
from webportal.map_website.get_skeleton import get_clean_urls_list


def get_main_website_urls(
    main_url: str, max_urls: int = 2, concurrency: int = 8
) -> list[str]:
    crawler = asyncio.run(
        crawl(main_url, max_urls * 3, max_depth=5, concurrency=concurrency)
    )
    tree_output = crawler.export_structure("tree")
    urls = get_clean_urls_list(tree_output)[:max_urls]
    return urls


def ingest_website(
    url: str,
    max_urls: int = 2,
    concurrency: int = 8,
    data_dir: Path = Path("data"),
    headless: bool = True,
) -> str:
    # Map the website
    urls = get_main_website_urls(url, max_urls, concurrency)
    ingestion_prompt = """
You are tasked with exploring all interactive elements of a website. Here is the initial url that you are exploring:
{url}

Your aim is to find all interactions that have not been found by our crawler (this crawler just gathered all the link elements form the HTML).
So you should try to explore all nontrivial interactions : select all interesting options in a form, click page selection, enable filters, etc.
We will then intercept network requests made during interactions : so if you're interacting with a form fo instance, make sure to submit it to trigger the request.
Clicking simple links is not useful, avoid it.

This will later be used to create a full functional graph from the website : so make sure to cover interactions that would be useful to common users.
Never bother explorint subpages of the initial page, because these will be explored by other agents, one per url : so once you've interacted a bit, you can go back to the initial url to explore other elements.
Go on ! Make sure to explore all the meaningful user interactions that one would expect to do from your starting page.
Don't do too much planning, just act.
When you're finished, return "I finished the exploration".
"""

    # Ingest the selected urls
    interactive_elements_gathered: list[str] = []
    for url in tqdm(urls):
        # Get the main domain from the url
        main_domain, path = urlparse(url).netloc, urlparse(url).path
        run_data_dir = (
            data_dir
            / main_domain
            / datetime.now().strftime("%Y-%m-%d")
            / path.replace("/", "_")
        )
        if not run_data_dir.exists():
            run_data_dir.mkdir(parents=True, exist_ok=True)
        interactive_elements_gathered_url = ingest_from_prompt(
            ingestion_prompt.format(url=url), run_data_dir, headless=headless
        )
        interactive_elements_gathered.append(interactive_elements_gathered_url)
        print(f"Ingested {url}, and got these elements:")
        print(interactive_elements_gathered_url)

    # Aggregate elements into API docs
    print("Aggregating elements into API docs")
    api_docs_conversion_prompt = create_api_docs_conversion_prompt(
        "\n\n".join(interactive_elements_gathered)
    )
    clean_ap_docs = call_llm(api_docs_conversion_prompt)
    return clean_ap_docs


if __name__ == "__main__":
    ingest_website("arxiv.org", 10, 8, Path("data"), headless=True)
