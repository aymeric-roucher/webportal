# Webportal: Website to API Documentation Converter

## The Big Idea
Imagine you're an AI agent trying to book a flight on Expedia or search GitHub issues. Instead of having to navigate the website like a human (clicking buttons, filling forms), you could just make direct API calls. But most websites don't publish their APIs.

**Webportal solves this**: Give it any website URL, and it will reverse-engineer that site into clean API documentation by automating a browser to interact with the site while capturing all the underlying network requests. The result is structured markdown docs showing exactly which API calls to make instead of web scraping.

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

## Two-Backend Architecture
Use a clean separation of concerns with two backend services:

1. **Frontend + Auth Backend**: React/Vite/Tailwind/Supabase
   - Handles user authentication and management
   - Job tracking and status updates
   - File storage for screenshots and results
   - Cache management for processed sites
   - Credit/payment system with Stripe
   - Real-time subscriptions for live updates

2. **Processing Backend**: Python FastAPI Service (existing codebase)
   - Pure website processing and ingestion
   - Receives requests from Supabase
   - Runs automated browser sessions
   - Sends status updates via webhooks to Supabase
   - Deploy separately (Railway/Render/DigitalOcean)

## Frontend User Experience

### 1. **Landing Experience**
- Clean, focused homepage explaining the concept with examples
- "Convert any website into API docs" tagline
- Demo video/GIFs showing the live processing
- Pricing: 3 free conversions, then pay-per-use
- Live examples of popular sites already processed

### 2. **Main Conversion Interface**

**URL Input Screen:**
- Large URL input field with validation
- Optional "Interaction Instructions" textarea (e.g., "Click the login button then search for Python repositories")
- "Convert Website" button
- Instant feedback if site already processed (cache hit) → direct download

**Live Processing Dashboard:**
- Real-time progress bar (0-100%)
- Current step description ("Starting browser", "Clicking search button", "Analyzing network requests")
- **Live screenshot carousel** showing what the automated browser is doing right now
- Estimated time remaining
- Cancel button
- WebSocket connection for real-time updates

**Results Screen:**
- Markdown preview of generated API documentation
- Download button for .md file
- Share/bookmark functionality
- Export options (Postman collection, OpenAPI spec)
- "Process Another Site" button

### 3. **User Dashboard**
- **Processing History**: List of all converted sites with status, download links, re-process options
- **Credits Management**: Current balance, purchase more credits
- **Cached Sites**: Browse previously processed sites by all users (public cache)
- **Account Settings**: Profile, billing, usage stats

### 4. **Real-time Features**
- **WebSocket connection** for live updates during processing
- **Screenshot streaming** - see the automated browser in action
- **Progress notifications** - browser notifications when job completes
- **Error handling** - graceful failures with retry options

## Technology Stack Guidelines

### Frontend Stack
- **Framework**: React 18+ with Vite
- **Styling**: Tailwind CSS with component library (shadcn/ui recommended)
- **State Management**: Zustand or React Query for server state
- **Real-time**: Supabase real-time subscriptions
- **Routing**: React Router v6
- **Forms**: React Hook Form with Zod validation
- **UI Components**: Modern, clean design similar to RunwayML or Midjourney

### Backend Modifications (Python)
You can modify the existing Python code to:
- Add FastAPI endpoints for external integration
- Implement webhook system for status updates
- Add proper job queuing with Redis/Celery
- Enhance caching mechanism with database storage
- Add file upload to cloud storage (Supabase Storage/S3)

### Deployment Structure
```
Frontend (Lovable/Vercel)
├── React/Vite app
└── Connected to Supabase

Supabase (Managed)
├── Auth & User Management
├── Database (jobs, cache, users)
├── Storage (screenshots, results)
├── Edge Functions (webhooks)
└── Real-time subscriptions

Python API (Railway/Render)
├── FastAPI server
├── Selenium automation
├── Docker container
└── Webhook integration
```

### Key User Experience Principles
- **Transparency**: Live screenshot feed shows AI agent working
- **Speed**: Instant cache hits for repeat sites
- **Trust**: Clear progress indicators and error messages
- **Value**: Generated docs are immediately useful with code examples
- **Scalability**: Credit system supports freemium model

The frontend should feel like a modern SaaS tool where the processing feels magical with live visual feedback, results are immediately useful, and the cache system makes repeat visits instant.