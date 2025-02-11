import aiohttp
import asyncio
import re
from trafilatura import extract, extract_metadata
from langchain_core.documents import Document

from .errors import ExtractionError
from .models import ArticleMetadata


async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch and clean content from a single URL."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text(encoding="utf-8")
            else:
                raise ExtractionError(url, f"Status {response.status}")
    except ExtractionError:
        raise
    except Exception as e:
        raise ExtractionError(url, str(e))
    
def format_content(url: str, html: str):
    """Format the content of a URL."""

    # Extract main content using trafilatura
    # This automatically removes boilerplate, ads, navigation, etc.
    content = extract(
        html,
        url=url,
        favor_recall=True,
        include_comments=True,
        include_formatting=True,
        output_format="markdown",
        include_links=True,
        include_tables=True,
        include_images=False
    )

    if content is None:
        raise ExtractionError(url, "No content extracted")
    
    # Remove unintended line breaks, keeping double line breaks and lists
    content = re.sub(r'(\w|[*_])\n(?![\n\s-])', r'\1 ', content)

    metadata = extract_metadata(html).as_dict()
    metadata = ArticleMetadata(
        url=url,
        hostname=metadata.get("hostname"),
        title=metadata.get("title"),
        description=metadata.get("description"),
        license=metadata.get("license"),
        author=metadata.get("author")
    )

    return Document(
        content,
        metadata=metadata
    )

async def scrape_urls(urls: list[str]) -> list[Document]:
    """Scrape multiple URLs concurrently."""
    # Configure client session with appropriate headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        results = await asyncio.gather(*[fetch_url(session, url) for url in urls], return_exceptions=True)

    documents: list[Document] = []
    for url, result in zip(urls, results, strict=True):
        if isinstance(result, ExtractionError):
            print(f"Error extracting {url}: {result}")
            continue
        
        document = format_content(url, result)
        documents.append(document)

    return documents
        