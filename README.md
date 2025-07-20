# WebPortal

A Python package for extracting static content and dynamic elements from webpages, designed to simplify the work of AI agents interacting with websites.

## Features

- **Static Content Extraction**: Extract and convert webpage content to markdown
- **Dynamic Element Detection**: Find buttons, forms, links, and input fields
- **Network Request Interception**: Capture API endpoints and network requests
- **AI Agent Tools**: Generate interaction tools for AI agents
- **Markdown Output**: Create simplified markdown summaries for AI consumption

## Installation

```bash
# Install the package
pip install -e .

# Install Playwright browsers
playwright install chromium
```

## Quick Start

### Command Line Interface

```bash
# Basic crawling
python -m webportal.cli https://example.com

# With network interception
python -m webportal.cli https://example.com --network

# Save to specific file
python -m webportal.cli https://example.com -o my_page.md

# Run in visible mode (for debugging)
python -m webportal.cli https://example.com --no-headless
```

### Python API

```python
import asyncio
from webportal import crawl_website, crawl_with_network

async def main():
    # Basic crawling
    data = await crawl_website("https://example.com")
    print(f"Found {len(data.dynamic_elements)} dynamic elements")
    
    # Network-aware crawling
    data = await crawl_with_network("https://example.com")
    print(f"Captured {len(data.network_requests)} network requests")
    print(f"Generated {len(data.interaction_tools)} interaction tools")

asyncio.run(main())
```

## Usage Examples

### Basic Web Crawler

```python
from webportal import WebCrawler

async with WebCrawler() as crawler:
    data = await crawler.crawl_page("https://example.com")
    
    print(f"Title: {data.title}")
    print(f"Static content: {data.static_content[:200]}...")
    
    for element in data.dynamic_elements:
        print(f"{element.type}: {element.text}")
```

### Network-Aware Crawler

```python
from webportal import NetworkAwareCrawler

async with NetworkAwareCrawler() as crawler:
    data = await crawler.crawl_with_interactions("https://example.com")
    
    # Access network requests
    for request in data.network_requests:
        print(f"{request.method} {request.url}")
    
    # Access interaction tools
    for tool in data.interaction_tools:
        print(f"Tool: {tool['name']} - {tool['description']}")
```

## Output Format

The package generates markdown files with the following structure:

```markdown
# Page Title
**URL:** https://example.com

## Static Content
Extracted text content from the page...

## Available Tools
Use these tools to interact with the page:

### click_submit_button
**Description:** Click the 'Submit' button
**Action:** click
**Selector:** #submit-btn

### fill_username
**Description:** Fill the 'username' input field
**Action:** fill
**Field:** username
**Type:** text
**Placeholder:** Enter username

## API Endpoints Discovered
- **POST** https://api.example.com/login
  - Status: 200
  - Content-Type: application/json

## Interactive Elements Found
### Buttons (3)
- Submit
- Cancel
- Reset
```

## Data Structures

### WebPageData
```python
@dataclass
class WebPageData:
    url: str
    title: str
    static_content: str
    dynamic_elements: List[DynamicElement]
    api_endpoints: List[Dict[str, Any]]
    markdown_summary: str
```

### DynamicElement
```python
@dataclass
class DynamicElement:
    type: str  # button, form, link, input, etc.
    selector: str
    text: str
    attributes: Dict[str, str]
    action: str  # click, submit, input, etc.
    url: Optional[str] = None
    method: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
```

## Configuration

### Browser Options
- `headless`: Run browser in headless mode (default: True)
- `wait_time`: Time to wait for dynamic content (default: 3000ms)

### Network Interception
The network-aware crawler automatically:
- Captures all HTTP requests and responses
- Identifies API endpoints based on URL patterns and headers
- Performs sample interactions to trigger additional requests

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/
```

## Examples

See `src/webportal/example.py` for complete usage examples.

## License

MIT License
