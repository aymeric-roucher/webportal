import asyncio
import tempfile
import textwrap
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
from smolagents import InferenceClientModel, tool
from tqdm import tqdm

from webportal.get_interactive.convert_to_api_docs import (
    create_api_docs_conversion_prompt,
)
from webportal.get_interactive.ingest_page import INGESTION_PROMPT, ingest_page
from webportal.get_interactive.network_capture import SeleniumVisionAgent
from webportal.inference import call_llm
from webportal.map_website.crawl import crawl
from webportal.map_website.get_skeleton import get_clean_urls_list


def get_main_website_urls(
    main_url: str, max_urls: int, concurrency: int, max_pages: int, max_depth: int
) -> list[str]:
    crawler = asyncio.run(
        crawl(
            url=main_url,
            max_pages=max_pages,
            max_depth=max_depth,
            concurrency=concurrency,
        )
    )
    tree_output = crawler.export_structure("tree")
    urls = list(set(get_clean_urls_list(tree_output)))[:max_urls]
    return urls


def list_possible_workflows_from_url(
    url: str,
    headless: bool = True,
) -> list[str]:
    activities_listing_prompt = textwrap.dedent("""Please list all possible interaction flows that could be started by common users on the webpage that you see below.
        For instance '**Search workflow** - open the Advanced search button, enable filters, then trigger the search' is an interaction flow.
        Exclude from your listing any interactions that are just about clicking links and navigating. Also exclude anything login-related.
        Don't perform them, only return the list using final_answer. Each item in the list you provide must be a full workflow.""")

    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-32B-Instruct",
        provider="auto",
    )

    @tool
    def final_answer(activities: list[str]) -> list:
        """Returns the list of actions to do from the current webpage

        Args:
            activities: list[str]
        """
        return activities

    with tempfile.TemporaryDirectory() as temp_dir:
        selenium_vision_agent = SeleniumVisionAgent(
            model=model,
            data_dir=str(temp_dir),
            tools=[final_answer],
            max_steps=3,
            browser_headless=headless,
        )
        selenium_vision_agent.tools["final_answer"] = final_answer
        screenshot = selenium_vision_agent.quick_open_url(url)
        activities = selenium_vision_agent.run(
            activities_listing_prompt, images=[screenshot]
        )
        selenium_vision_agent.close()
    return activities


def ingest_single_page(
    url: str,
    data_dir: Path,
    headless: bool = True,
    domain_name: str | None = None,
) -> str:
    workflows = list_possible_workflows_from_url(url, headless=headless)
    print(f"Workflows for {url}: {workflows}")

    # Get the main domain from the url
    path = urlparse(url).path
    run_data_dir = (
        data_dir
        / domain_name
        / datetime.now().strftime("%Y-%m-%d")
        / path.strip("/").replace("/", "_")
    )
    if not run_data_dir.exists():
        run_data_dir.mkdir(parents=True, exist_ok=True)
    interactive_elements_gathered_url = ingest_page(
        url,
        run_data_dir,
        headless=headless,
        domain_to_stay_on=domain_name,
        custom_prompt=INGESTION_PROMPT.format(target_url=url)
        + "\nHere are some workflows that you can explore: "
        + "\n".join(workflows),
    )
    print(f"Ingested {url}, and got these elements:")
    print(interactive_elements_gathered_url)
    return interactive_elements_gathered_url




def ingest_website(
    main_url: str,
    max_urls: int = 100,
    concurrency: int = 8,
    data_dir: Path = Path("data"),
    headless: bool = True,
    nb_pages: int = 100,
    max_depth: int = 5,
) -> str:
    # Map the website
    if not main_url.startswith(("http://", "https://")):
        main_url = f"https://{main_url}"
    domain_name = urlparse(main_url).netloc
    urls = get_main_website_urls(
        main_url=main_url,
        max_urls=max_urls,
        concurrency=concurrency,
        max_pages=nb_pages,
        max_depth=max_depth,
    )
    print(f"Found {len(urls)} urls to ingest:")
    print("\n".join(urls))

    # Ingest the selected urls sequentially
    interactive_elements_gathered: list[str] = []

    for url in tqdm(urls, desc="Ingesting URLs"):
        interactive_elements_gathered_url = ingest_single_page(
            url, data_dir, headless, domain_name
        )
        if interactive_elements_gathered_url:
            interactive_elements_gathered.append(interactive_elements_gathered_url)
        else:
            print(f"Error ingesting {url}")

    # Aggregate elements into API docs
    print("Aggregating elements into API docs")
    api_docs_conversion_prompt = create_api_docs_conversion_prompt(
        "\n\n".join(interactive_elements_gathered)
    )
    clean_ap_docs = call_llm(api_docs_conversion_prompt)
    with open(data_dir / domain_name / "api_docs.md", "w") as f:
        f.write(clean_ap_docs)
    print(f"API docs written to {data_dir / domain_name / 'api_docs.md'}")
    return clean_ap_docs


if __name__ == "__main__":
    output = ingest_website(main_url="castorama.fr")
