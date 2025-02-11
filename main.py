from pathlib import Path

import typer

from src.cli import UTyper

app = UTyper(name="News Extractor")


@app.command(
    short_help="Extract, summarize, and save news articles from the given sources (URLs)",
    help="""Extract, summarize, and save news articles from the given sources.
        The sources can be provided with a list of URLs or a file with a list of URLs.

        URLs can omit the protocol (http or https). In this case, https is assumed.
        """,
)
async def extract(
    urls: list[str] | None = typer.Option(
        None, help="A URL or a list of URLs to extract news from."
    ),
    urls_file: Path | None = typer.Option(
        None, help="Path to the file containing the list of URLs to extract news from."
    ),
    dry_run: bool = typer.Option(
        False, help="If set, the saving of the extracted news will not be done."
    ),
):
    from langchain_openai import ChatOpenAI

    from src.scraping import scrape_urls, validate_urls
    from src.settings import settings
    from src.storage import database
    from src.summarization import summarize

    if not urls and not urls_file:
        raise typer.Abort(
            "No URL or file with URLs provided. Please provide either a URL or a file with URLs."
        )

    if urls and urls_file:
        raise typer.Abort(
            "Both URL and file with URLs provided. Please provide only one."
        )

    if urls_file:
        try:
            with open(urls_file, "r") as f:
                urls = f.readlines()
        except FileNotFoundError:
            raise typer.Abort(
                f"Unable to read the file: {urls_file}. Please make sure the file exists and it can be read."
            )

    urls = validate_urls(urls)
    print(f"Validated {len(urls)} URLs.")

    documents = await scrape_urls(urls)

    llm: ChatOpenAI = ChatOpenAI(
        base_url=settings.llm.base_url,
        model=settings.llm.model,
    )

    for i, document in enumerate(documents):
        print(f"[{i}] Summarizing document '{document.metadata['url']}'...")
        summarization = await summarize(document, llm)

        print(f"[{i}] Saving summarization to the database...")
        database.add(document, summarization)


@app.command(
    short_help="Search for related articles in the database of extracted content",
    help="Search for related articles in the database of extracted content. The search is based on the semantic similarity of the articles.",
)
def search(query: str):
    from src.storage import database

    articles = database.search(query)

    if not articles:
        return

    print(f"Found {len(articles)} articles related to the query:")
    for i, article in enumerate(articles):
        print(f"[{i + 1}] {article}")


@app.command(
    short_help="Print all existing topics, articles and their summaries.",
    help="Explore the current data, printing all existing topics, articles and their summaries.",
)
def explore():
    from src.storage import database

    topics, articles = database.get_all()
    if not topics:
        print("No topics found in the database.")
    else:
        print(f"Found {len(topics)} topics in the database.")
        for code, topic in topics.items():
            print(f" - '{topic}' ({code})")

    if not articles:
        print("No articles found in the database.")
    else:
        print(f"\nFound {len(articles)} articles in the database.")
        for i, article in enumerate(articles):
            print(f"[{i + 1}] {article}")


if __name__ == "__main__":
    app()
