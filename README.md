# News scraping

A Python-based tool for extracting, summarizing, and analyzing news articles using Large Language Models (LLM) and vector search capabilities.

This is a very early stage implementation that is not friendly for the end-users. Please expect the CLI to change and the code to be better documented in the next couple of days.

## Internals

The following notes describe the internal structure and the decision behind that structure.

- The reason behind separating `articles`, `summaries` and `topics` collections is to be able to search by each of them separately. So that a semantic search query can match with a topic that brings all related articles as well in the response. Unfortunately, it seems to be harder than I expected with Chroma. I'm searching for a solution.
- The way of extracting (scraping and formatting) the content of news can dramatically change based on the target platforms / websites it is used for. Right now a very simple aiohttp request with trafilatura seems to be enough to get the job done. For more complex behavior browser simulation and automation might be used.


## ToDo

The following to-do list is ordered by priority.

- [Feature] Implement separate search by topics & summaries. An article with corresponding topic should be returned even if the search query distance is above the article threshold.
- [Performance] Implement the async communication with the vector database and refactor data read & update with parallel execution.
- [Feature] Create Dockerfile with .devcontainer startup configuration for faster testing.
- [Extra] Better exception and edge cases handling (websites 404, runtime errors, configuration errors, etc.)
- [Extra] Implement a proper logging system with debug/warning information.
- [Extra] Add pytests for basic logic.

## Getting Started

### Prerequisites

- Python 3.12
- Access to an LLM API (configured via `config.toml` and environment variables)
