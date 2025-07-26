# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Webportal is a Python project that converts websites into agent-friendly interfaces by:
1. Using a smolagents web agent to navigate websites
2. Looking at the network requests made by the agent to extract the API calls
3. Describing those API calls so that any agent that want to access that specific ressource can directly do it using the API calls instead of having to crawl the website again.

The output must be a markdown file that describes the API calls and how to use them. 

For instance, if the website is github the output must be a markdown file that explains how to search a repository, how to get the issues of a repository, how to get the labels of an issue, ect... So that any agent that want to access that specific ressource can directly do it using the API calls instead of having to crawl the website again.

## Key Development Commands

### Testing
```bash
pytest                           # Run all tests
pytest tests/test_selenium.py    # Run selenium-specific tests
pytest -m expensive            # Run expensive/slow tests (like Selenium)
```

### Python Environment
```bash
uv sync                         # Install dependencies (uses uv.lock)
python -m pytest               # Alternative test runner
```


## Architecture

### Core Processing Pipeline
1. **HAR Extraction** (`har_extractor.py`): Converts HAR files from browser network logs into structured API definitions with endpoints, parameters, headers, and response patterns
2. **Tool Generation** (`json_to_tools.py`): Transforms API JSON into Python functions decorated with `@tool` for smolagents framework
3. **Agent Execution** (`agent.py`): Runs CodeAgent with generated tools and base HTTP request tools (`get_request`, `post_request`)

### Two Automation Approaches

**Static/API-based** (`agent.py`):
- Uses extracted API calls from HAR files
- Provides `get_request` and `post_request` tools with proper headers
- Supports both JSON and HTML responses with BeautifulSoup parsing
- GraphQL error handling built-in

**Interactive/Browser-based** (`src/webportal/get_interactive/selenium_agent.py`):
- `SeleniumVisionAgent` extends CodeAgent with browser automation
- Provides comprehensive desktop interaction tools (click, type, scroll, etc.)
- Network monitoring via Chrome DevTools Protocol
- Screenshot capture with click markers for debugging

### Project Structure
- `digested_websites/` - Website-specific processed content
- `data/` - Screenshot storage for Selenium agent
- `src/webportal/` - Main package code
- `src/webportal/get_interactive/` - Selenium agent code that will crawl a website to extract the relevant API calls. 
- `tests/` - Test files with Selenium integration tests

### Main Dependencies
- **smolagents**: Agent framework with Qwen model integration
- **selenium**: Browser automation with Chrome driver
- **requests**: HTTP client for API interactions

### Coding Style
- DO NOT USE TRY/EXCEPT blocks except if it is absolutely necessary (meaning that this is the only way to handle the error). And in that case, you should except a specific error.
- This is python3.13 code so DO NOT use "List" or "Dict" for typing, use "list" or "dict" instead. 
- Typing is important
- Always choose the simplest solutions that will do the job.
