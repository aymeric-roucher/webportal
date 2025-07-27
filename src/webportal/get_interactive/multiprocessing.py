import multiprocessing
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from webportal.common import DATA_PATH
from webportal.get_interactive.ingest_page import ingest_page


@dataclass
class IngestTask:
    """Configuration for a single ingest task."""

    prompt: str
    data_dir: Path


def _page_ingest_worker(task_and_headless: tuple[IngestTask, bool]) -> str:
    """Worker function for multiprocessing - must be at module level for pickling."""
    task, headless = task_and_headless
    # Add unique suffix to avoid directory conflicts
    unique_data_dir = task.data_dir / str(uuid.uuid4())
    result = ingest_page(task.prompt, unique_data_dir, headless)
    return result


def run_multiple_ingests(
    tasks: list[IngestTask], max_workers: int | None = None, headless: bool = True
) -> list[str]:
    """Run multiple ingest_from_prompt functions concurrently.

    Args:
        tasks: list of IngestTask dataclass instances
        max_workers: Maximum number of concurrent processes (defaults to CPU count)
        headless: Whether to run browsers in headless mode

    Returns:
        list of API documentation strings in the same order as input
    """
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(_page_ingest_worker, (tasks[i], headless)): i
            for i in range(len(tasks))
        }

        # Collect results maintaining order
        ordered_results = [None] * len(tasks)
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            result = future.result()
            ordered_results[index] = result

    return ordered_results


if __name__ == "__main__":
    # Example of running single ingest
    prompt = """
According to github, when was Regression added to the oldest closed numpy.polynomial issue that has the Regression label in MM/DD/YY?
                              
Start by going to the numpy package page and then click on the Issues tab.
"""
    data_dir = DATA_PATH / "github"

    # Single run
    # result = ingest_from_prompt(prompt, data_dir)

    # Example of running multiple ingests concurrently
    tasks = [
        IngestTask(prompt=prompt, data_dir=DATA_PATH / "github"),
        IngestTask(prompt=prompt, data_dir=DATA_PATH / "github"),
        # Add more IngestTask instances here for concurrent execution
    ]

    results = run_multiple_ingests(tasks, max_workers=2, headless=True)
    for i, result in enumerate(results):
        print(f"Result {i}: {result[:100]}...")  # Print first 100 chars
