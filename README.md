# Webportal

Make your website agent-accessible.

## Workflow

1. **Manual navigation on a website** - Browse the website manually to explore it and cover as much as possible / desired 
2. **Extract HAR file** - Manually extract the HAR file containing all API calls (in Google Chrome)
3. **Process HAR file** - Use `har_extractor.py` to convert the HAR file into a JSON file of existing APIs
4. **Convert to tools** - Use `json_to_tools.py` to convert the JSON file into a list of smolagents tools (Python functions with docstrings and `@tool` decorator)
5. **Agent interaction** - Use `agent.py` to answer questions or do work on the considered website by manually editing the "task" prompt at the end of the file

## Thoughts

- **API count**: Number of APIs seems reasonable (maybe 100 for GitHub???)
- **LLM limitations**: LLMs are good at "translating" .har into .json and into .py (but not deterministic, slow and expensive) = can be used for experimentations but should be avoided for production

## Docker

Building the container:
```bash
docker build --platform linux/amd64 -t webportal-selenium . 
```

Running the container (sharing the src folder allows to instantly propagate changes to the docker):
```bash
source .env && docker run -it --rm --platform linux/amd64 --ulimit nofile=32768 \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -e HF_TOKEN=$HUGGINGFACE_API_KEY \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/src:/app/src" \
    webportal-selenium
```

**Note**: Container auto-removes after exit (`--rm`). Selenium Grid starts automatically for multiprocessing support.

### Testing Multiprocessing

```bash
docker run --rm --platform linux/amd64 --ulimit nofile=32768 \
    -v "$(pwd)/test_grid_multiprocessing.py:/app/test_grid_multiprocessing.py" \
    webportal-selenium \
    /bin/bash -c "/opt/bin/start-selenium-standalone.sh & sleep 5 && uv run python test_grid_multiprocessing.py"
```

# Aymeric to Charles

### Which sites to scrape first

The 5 Most Frequent Domains:
nas.er.usgs.gov - 3 questions
wikipedia.org - 3 questions
arxiv.org - 2 questions
nature.com - 2 questions
metmuseum.org - 2 questions

9 out of 27 questions (33.3%) can be completely solved using only these top 5 domains.

### I've broken selenium

Running the above command (runs `src/webportal/ingest.py`) works fine at first with multiple agents in parallel.
But then during the core agent run that tries to get network requests, the run fails as follows:
```
╭────────────────────────────────────────────────────────── New run ──────────────────────────────────────────────────────────╮
│                                                                                                                             │
│ You are tasked with exploring all interactive elements of the following webpage: https://arxiv.org/search/advanced          │
│ Your browser is already open at this initial page, and a screenshot is shown below.                                         │
│                                                                                                                             │
│ Your aim is to find all interactions that have not been found by our crawler (this crawler just gathered all the link       │
│ elements form the HTML).                                                                                                    │
│ So you should try to explore all nontrivial interactions : select all interesting options in a form, click page selection,  │
│ enable filters, etc.                                                                                                        │
│ We will then intercept network requests made during interactions : so if you're interacting with a form for instance, make  │
│ sure to submit it to trigger the request.                                                                                   │
│ Clicking simple links is not useful, avoid it.                                                                              │
│                                                                                                                             │
│ This will later be used to create a full functional graph from the website : so make sure to cover interactions that would  │
│ be useful to common users.                                                                                                  │
│ Never bother exploring subpages of the initial page, because these will be explored by other agents, one per url : so once  │
│ you've tried some interaction or your interactions brought you to a new page, you can use open_url to go back to the        │
│ initial url, then explore other elements.                                                                                   │
│ Go on ! Make sure to explore all the meaningful user interactions that one would expect to do from your starting page. A    │
│ good rule of thumb is to try at least 3 different interaction flows.                                                        │
│ Don't do too much planning.                                                                                                 │
│ When you're finished, return "I finished the exploration".                                                                  │
│                                                                                                                             │
│ Here are some workflows that you can explore: **Search Workflow** - Users enter search terms in the 'Search term(s)' field, │
│ choose a relevant category (e.g., Title, Author), select appropriate subject filters (e.g., Computer Science, Physics), and │
│ click the 'Search' button to generate results. Users may refine their search using multiple terms and additional filters.   │
│ **Subject Filtering Workflow** - Users can explore content by selecting specific subject categories (e.g., Physics,         │
│ Economics, Engineering). They can perform searches within these categories either using general keywords or author names,   │
│ and add multiple categories as needed to broaden their search scope.                                                        │
│ **Detailed Author Search Workflow** - Users can use the guidelines in the sidebar to enter author names accurately (e.g.,   │
│ with specific patterns like surname and initials). They can then search for publications authored by these individuals,     │
│ with options to specify the exact format (e.g., enclosed in quotes for exact matches).                                      │
│ **Refinement Workflow** - Advanced users may utilize multiple search terms and subject categories simultaneously to refine  │
│ their search queries. They can add additional search fields if needed to achieve more precise results. This workflow        │
│ involves stepping through the page incrementally, setting up each aspect of the search carefully.                           │
│                                                                                                                             │
╰─ InferenceClientModel - Qwen/Qwen2.5-VL-32B-Instruct ───────────────────────────────────────────────────────────────────────╯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Step 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Short term goal: I want to explore the search workflow by entering a search term and submitting the form. What I see: The      
screenshot shows the arXiv advanced search page with a search term input field, subject checkboxes, and a 'Search' button.     
There is also guidance on the right regarding author searches. Reflection: The initial step in the search workflow is to enter 
a search term. I will do that and proceed to submit the form to generate results. Action: {"name": "type_text", "arguments":   
{"text": "artificial intelligence", "target_description": "search term input field, white rectangular text box with placeholder
text 'Search term...', located below the 'Search term(s)' label"}}                                                             
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Calling tool: 'type_text' with arguments: {'text': 'artificial intelligence', 'target_description': "search term input      │
│ field, white rectangular text box with placeholder text 'Search term...', located below the 'Search term(s)' label"}        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Typed text: 'artificial intelligence' in: search term input field, white rectangular text box with placeholder text 'Search 
term...', located below the 'Search term(s)' label
Observations: Typed text: 'artificial intelligence' in: search term input field, white rectangular text box with placeholder 
text 'Search term...', located below the 'Search term(s)' label
Analyzing screen content...
Saved screenshot for step 1 to data/arxiv.org/2025-07-27/search_advanced/step_001.png
Capturing network requests for step 1
concurrent.futures.process._RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/usr/lib/python3.13/concurrent/futures/process.py", line 254, in _process_worker
    r = call_item.fn(*call_item.args, **call_item.kwargs)
  File "/app/src/webportal/ingest.py", line 113, in _url_ingest_worker
    result = ingest_single_page(url, data_dir, headless, domain_name)
  File "/app/src/webportal/ingest.py", line 96, in ingest_single_page
    interactive_elements_gathered_url = ingest_page(
        url,
    ...<5 lines>...
        + "\n".join(workflows),
    )
  File "/app/src/webportal/get_interactive/ingest_page.py", line 55, in ingest_page
    selenium_vision_agent.run(ingestion_prompt, images=[screenshot])
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/smolagents/agents.py", line 467, in run
    steps = list(self._run_stream(task=self.task, max_steps=max_steps, images=images))
  File "/app/.venv/lib/python3.13/site-packages/smolagents/agents.py", line 566, in _run_stream
    self._finalize_step(action_step)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/smolagents/agents.py", line 585, in _finalize_step
    self.step_callbacks.callback(memory_step, agent=self)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/smolagents/memory.py", line 297, in callback
    cb(memory_step) if len(inspect.signature(cb).parameters) == 1 else cb(memory_step, **kwargs)
                                                                       ~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/webportal/get_interactive/network_capture.py", line 161, in capture_requests_callback
    step_requests = self.capture_step_network_activity(current_step)
  File "/app/src/webportal/get_interactive/network_capture.py", line 80, in capture_step_network_activity
    logs = self.driver.get_log("performance")
           ^^^^^^^^^^^^^^^^^^^
AttributeError: 'WebDriver' object has no attribute 'get_log'
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/app/src/webportal/ingest.py", line 173, in <module>
    output = ingest_website("arxiv.org", 20, 4, Path("data"), headless=True)
  File "/app/src/webportal/ingest.py", line 152, in ingest_website
    result = future.result()
  File "/usr/lib/python3.13/concurrent/futures/_base.py", line 449, in result
    return self.__get_result()
           ~~~~~~~~~~~~~~~~~^^
  File "/usr/lib/python3.13/concurrent/futures/_base.py", line 401, in __get_result
    raise self._exception
AttributeError: 'WebDriver' object has no attribute 'get_log'
```

This is because I replaced the base selenium driver with a remote that connects to selenium grid.
IMO the simplest solution will be to switch to playwright.