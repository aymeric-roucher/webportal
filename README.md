# Automator

A project to turn a website into an agent-friendly one.

## Workflow

1. **Manual navigation on a website** - Browse the website manually to explore it and cover as much as possible / desired 
2. **Extract HAR file** - Manually extract the HAR file containing all API calls (in Google Chrome)
3. **Process HAR file** - Use `har_extractor.py` to convert the HAR file into a JSON file of existing APIs
4. **Convert to tools** - Use `json_to_tools.py` to convert the JSON file into a list of smolagents tools (Python functions with docstrings and `@tool` decorator)
5. **Agent interaction** - Use `agent.py` to answer questions or do work on the considered website by manually editing the "task" prompt at the end of the file

## Thoughts

- **API count**: Number of APIs seems reasonable (maybe 100 for GitHub???)
- **LLM limitations**: LLMs are good at "translating" .har into .json and into .py (but not deterministic, slow and expensive) = can be used for experimentations but should be avoided for production
