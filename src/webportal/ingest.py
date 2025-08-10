import asyncio
import tempfile
import textwrap
import time
import traceback
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
from smolagents import InferenceClientModel, tool
from tqdm import tqdm

from webportal.secret_manager import get_huggingface_token

from webportal.get_interactive.convert_to_api_docs import (
    create_api_docs_conversion_prompt,
)
from webportal.get_interactive.ingest_page import INGESTION_PROMPT, ingest_page
from webportal.get_interactive.network_capture import SeleniumVisionAgent
from webportal.inference import call_llm
from webportal.map_website.crawl import crawl
from webportal.map_website.get_skeleton import get_clean_urls_list
from webportal.storage_utils import (
    write_job_file_to_storage,
)
import yaml


def get_main_website_urls(
    main_url: str, max_urls: int, concurrency: int, max_pages: int, max_depth: int, 
    domain_name: str, job_id: str
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
    
    # Save site structure using job-specific storage
    write_job_file_to_storage(
        domain_name=domain_name, 
        job_id=job_id, 
        filename="site_structure.txt", 
        content=tree_output
    )
    
    urls = list(set(get_clean_urls_list(tree_output)))
    
    # Save URLs before trimming using job-specific storage
    urls_yaml = yaml.dump({"urls": urls})
    write_job_file_to_storage(
        domain_name=domain_name, 
        job_id=job_id, 
        filename="urls_before_trimming.yaml", 
        content=urls_yaml
    )
        
    # save also urls after trimming
    return urls[:max_urls]


def list_possible_workflows_from_url(
    url: str,
    headless: bool,
    data_dir: Path,
    domain_name: str,
    job_id: str,
    folder_name: str = "workflows",
) -> list[str]:
    activities_listing_prompt = textwrap.dedent("""Please list all possible interaction flows that could be started by common users on the webpage that you see below.
        For instance '**Search workflow** - open the Advanced search button, enable filters, then trigger the search' is an interaction flow.
        Exclude from your listing any interactions that are just about clicking links and navigating. Also exclude anything login-related.
        Don't perform them, only return the list using final_answer. Each item in the list you provide must be a full workflow.""")

    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider="nebius",
        token=get_huggingface_token(),
    )

    @tool
    def final_answer(activities: list[str]) -> list:
        """Returns the list of actions to do from the current webpage

        Args:
            activities: list[str]
        """
        return activities
    

    selenium_vision_agent = SeleniumVisionAgent(
        model=model,
        data_dir=data_dir,
        tools=[final_answer],
        max_steps=3,
        browser_headless=headless,
        domain_name=domain_name,
        job_id=job_id,
        folder_name=folder_name,
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
    job_id: str | None = None,
    folder_name: str | None = None,
) -> str:
    workflows = list_possible_workflows_from_url(url, data_dir=data_dir, headless=headless, domain_name=domain_name, job_id=job_id, folder_name=folder_name)
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
        target_url=url,
        data_dir=run_data_dir,
        headless=headless,
        custom_prompt=INGESTION_PROMPT.format(target_url=url)
        + "\nHere are some workflows that you can explore: "
        + "\n".join(workflows),
        domain_to_stay_on=domain_name,
        job_id=job_id,
        folder_name=folder_name,
    )
    print(f"Ingested {url}, and got these elements:")
    print(interactive_elements_gathered_url)
    return interactive_elements_gathered_url


def _create_job_id() -> str:
    """Create a unique job ID using timestamp"""
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def get_domain_name(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return urlparse(url).netloc

def ingest_website(
    main_url: str,
    max_urls: int = 100,
    concurrency: int = 8,
    data_dir: Path = Path("data"),
    headless: bool = True,
    nb_pages: int = 100,
    max_depth: int = 5,
    reload_from_saved: bool = False,
    job_id: str | None = None,
) -> str:

    domain_name = get_domain_name(main_url)
    if job_id is None:
        job_id = _create_job_id()
    
    print(f"Starting ingestion job: {job_id} for domain: {domain_name}")
    
    if reload_from_saved:
        from webportal.storage_utils import read_job_file_from_storage
        urls_content = read_job_file_from_storage(domain_name, job_id, "urls.yaml")
        urls_data = yaml.safe_load(urls_content)
        urls = urls_data["urls"]
        print(f"Reloaded {len(urls)} URLs from storage")
    else:
        urls = get_main_website_urls(
            main_url=main_url,
            max_urls=max_urls,
            concurrency=concurrency,
            max_pages=nb_pages,
            max_depth=max_depth,
            domain_name=domain_name,
            job_id=job_id,
        )
    
        # Save URLs using job-specific storage
        urls_yaml = yaml.dump({"urls": urls})
        write_job_file_to_storage(
            domain_name=domain_name, 
            job_id=job_id, 
            filename="urls.yaml", 
            content=urls_yaml
        )

    print(f"Found {len(urls)} urls to ingest:")
    print("\n".join(urls))
    # Ingest the selected urls sequentially
    interactive_elements_gathered: list[str] = []

    for url in tqdm(urls, desc="Ingesting URLs"):
        print(f"Ingesting {url}")
        # Create folder name based on URL path
        path = urlparse(url).path
        folder_name = path.strip("/").replace("/", "_") if path and path != "/" else "root"
        try:
            interactive_elements_gathered_url = ingest_single_page(
                url=url, 
                data_dir=data_dir, 
                headless=headless, 
                domain_name=domain_name, 
                job_id=job_id,
                folder_name=folder_name
            )
            if interactive_elements_gathered_url:
                interactive_elements_gathered.append(interactive_elements_gathered_url)
            else:
                print(f"No elements extracted from {url}")
        except Exception as e:
            error_message = f"Error ingesting {url}: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
            print(f"Error ingesting {url}: {str(e)}")
            
            # Save exception details to storage
            exception_filename = f"{folder_name}/exception_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            write_job_file_to_storage(
                domain_name=domain_name,
                job_id=job_id,
                filename=exception_filename,
                content=error_message
            )

    # Aggregate elements into API docs
    print("Aggregating elements into API docs")
    api_docs_conversion_prompt = create_api_docs_conversion_prompt(
        "\n\n".join(interactive_elements_gathered)
    )
    clean_ap_docs = call_llm(api_docs_conversion_prompt)
    
    # Save API docs using job-specific storage
    write_job_file_to_storage(
        domain_name=domain_name, 
        job_id=job_id, 
        filename="api_docs.md", 
        content=clean_ap_docs
    )
    
    print(f"Job {job_id} completed. API docs saved to storage.")
    return clean_ap_docs


if __name__ == "__main__":
    import os
    main_url = os.getenv("TARGET_WEBSITE", "clinicaltrials.gov")
    job_id = os.getenv("JOB_ID")
    print(f"Processing website: {main_url}")
    if job_id:
        print(f"Using job_id from environment: {job_id}")
    output = ingest_website(main_url=main_url, job_id=job_id)
