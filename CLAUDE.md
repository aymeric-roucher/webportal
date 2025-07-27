# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Webportal is a Python project that converts websites into agent-friendly interfaces by:
1. Using a smolagents web agent to navigate websites
2. Looking at the network requests made by the agent to extract the API calls
3. Describing those API calls so that any agent that want to access that specific ressource can directly do it using the API calls instead of having to crawl the website again.

For the user, it would enter a website url, and, either the site has already been processed in which cas it can download a markdown file. Otherwise, it will process the website and in the meantime provide a progress bar with images of the website being crawled.

### Coding Style
- DO NOT USE TRY/EXCEPT blocks except if it is absolutely necessary (meaning that this is the only way to handle the error). And in that case, you should except a specific error.
- This is python3.13 code so DO NOT use "List" or "Dict" for typing, use "list" or "dict" instead. 
- Typing is important
- Always choose the simplest solutions that will do the job.
