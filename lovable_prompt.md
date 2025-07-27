# Webportal: Website to API Documentation Converter

## The Big Idea
Imagine you're an AI agent trying to book a flight on Expedia or search GitHub issues. Instead of having to navigate the website like a human (clicking buttons, filling forms), you could just make direct API calls. But most websites don't publish their APIs.

**Webportal solves this**: Give it any website URL, and it will reverse-engineer that site into clean API documentation by automating a browser to interact with the site while capturing all the underlying network requests. The result is structured markdown docs showing exactly which API calls to make instead of web scraping.

## What the Frontend Should Do

### 1. **Landing Experience**
- Clean, focused homepage explaining the concept with examples
- "Convert any website into API docs" tagline
- Demo video/GIFs showing the process
- Pricing: 3 free conversions, then pay-per-use

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

**Results Screen:**
- Markdown preview of generated API documentation
- Download button for .md file
- Share/bookmark functionality
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

## Architecture (Two-Backend Approach)

### Frontend (React/Vite/Tailwind/Supabase)
Handles all user-facing features, auth, payments, job tracking, and real-time updates.

### Backend 1: Supabase (Auth & Data)
- User authentication and management
- Job tracking and status updates
- File storage for screenshots and results
- Cache management for processed sites
- Credit/payment system
- Real-time subscriptions for live updates

### Backend 2: Python Processing Service (External)
Your existing webportal Python codebase deployed separately that:
- Receives processing requests from Supabase
- Runs automated browser sessions with Selenium
- Captures network requests and screenshots
- Converts data to API documentation
- Sends status updates back to Supabase via webhooks

## Key User Experience Flows

### First-Time User
1. Land on homepage → see demo
2. Try with free credits
3. Enter URL → watch live processing with screenshots
4. Download API docs → amazed by results
5. Sign up to get more credits

### Power User
1. Login → dashboard shows processing history
2. Submit new URL → check if cached first
3. If not cached → queue for processing with live updates
4. Manage multiple jobs simultaneously
5. Browse and download from public cache

### Developer Integration
- Generated API docs include code examples
- Export options (Postman collection, OpenAPI spec)
- Webhook URLs for integration with other tools

## Technical Implementation Notes

The frontend should feel like a modern SaaS tool (think RunwayML or Midjourney) where:
- The processing feels magical with live visual feedback
- Results are immediately useful and well-formatted  
- The cache system makes repeat visits instant
- The credit system is transparent and fair

The key innovation is the **live screenshot feed** - users can literally watch the AI agent navigate the website in real-time, making the black box transparent and building trust in the results.