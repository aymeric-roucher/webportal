# Webportal: Website to API Documentation Converter

## Project Overview
Webportal is a Python application that reverse-engineers websites into structured API documentation by automating browser interactions and capturing underlying API calls. This enables AI agents to directly access website functionality via APIs instead of web scraping.

## Core Workflow
1. **Agent Navigation**: Uses smolagents with Selenium to interact with websites (clicking buttons, filling forms, etc.)
2. **Network Capture**: Monitors and captures all network requests made during interactions using Chrome DevTools Protocol
3. **API Documentation**: Converts captured requests into structured markdown documentation with examples
4. **Caching**: Stores processed results to avoid re-processing the same websites

## Current Architecture

### Backend Components
- **Core Engine** (`src/webportal/get_interactive/`):
  - `main.py`: Entry point for processing websites
  - `selenium_agent.py`: Browser automation with screenshot capabilities
  - `network_capture.py`: Network request monitoring and capture
  - `convert_to_api_docs.py`: Converts raw data to API documentation
  - `request_tools.py`: HTTP request utilities

- **Data Storage** (`data/` and `digested_websites/`):
  - Processed website data organized by domain
  - Screenshots of each interaction step
  - Generated markdown API documentation

- **Utilities**:
  - `inference.py`: LLM integration for content processing
  - `common.py`: Shared constants and configurations

### Dependencies
- **Web Automation**: Selenium WebDriver with Chrome
- **AI Models**: smolagents with support for various LLM providers
- **Network Monitoring**: Chrome DevTools Protocol
- **Data Processing**: BeautifulSoup, requests, markdownify

## Frontend/Backend Implementation Requirements

### Backend API Server
Build a FastAPI server that provides:

1. **Website Processing Endpoint**
   ```python
   POST /api/process-website
   Body: {"url": "https://example.com", "prompt": "optional interaction instructions"}
   Response: {"job_id": "uuid", "status": "processing"}
   ```

2. **Job Status Endpoint**
   ```python
   GET /api/jobs/{job_id}/status
   Response: {
     "status": "processing|completed|failed",
     "progress": 0.75,
     "current_step": "Clicking login button",
     "screenshots": ["step_001.png", "step_002.png"],
     "error_message": null
   }
   ```

3. **Results Download Endpoint**
   ```python
   GET /api/jobs/{job_id}/download
   Response: Markdown file with API documentation
   ```

4. **Cache Check Endpoint**
   ```python
   GET /api/check-cache/{domain}
   Response: {"cached": true, "file_path": "github.md", "last_updated": "2024-01-01"}
   ```

### Frontend Web Application
Build a React/Vite/Tailwind/Supabase interface with:

1. **URL Input Form**
   - URL validation
   - Optional interaction prompt textarea
   - Submit button

2. **Processing Dashboard**
   - Real-time progress bar
   - Current step description
   - Live screenshot carousel showing agent actions
   - WebSocket connection for real-time updates

3. **Results Display**
   - Markdown preview of generated API documentation
   - Download button for markdown file
   - Share/export options

4. **Cache Management**
   - List of previously processed websites
   - Re-process options
   - Cache invalidation controls

You can modify the python code if necessary, for instance for the caching mechanism.