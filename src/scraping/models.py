from typing import TypedDict


class ArticleMetadata(TypedDict):
    """Typed dictionary that describes the common metadata for an article Document."""

    url: str
    hostname: str

    title: str | None
    description: str | None
    license: str | None
    author: str | None
