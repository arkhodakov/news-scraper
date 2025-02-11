from typing import ClassVar

from chromadb import Collection, PersistentClient
from chromadb.api import ClientAPI
from langchain_core.documents import Document

from src.scraping.models import ArticleMetadata
from src.settings import settings
from src.summarization.summarize import ArticleSummarization

from .models import Article


class Database:
    """A very quick and simple implementation of the main methods to interact with the data.

    Chroma is currently used as a vector database due to its simplicity and local storage options."""

    default_collection_metadata: ClassVar[dict[str, any]] = {
        "hnsw:space": "cosine",
    }

    client: ClientAPI

    articles: Collection
    summaries: Collection
    topics: Collection

    def __init__(self):
        self.client = PersistentClient(
            path=settings.storage.path,
            tenant=settings.storage.tenant,
            database=settings.storage.database,
        )

        self.articles = self.client.get_or_create_collection(
            "articles",
            metadata=self.default_collection_metadata,
        )

        self.summaries = self.client.get_or_create_collection(
            "summaries",
            metadata=self.default_collection_metadata,
        )

        self.topics = self.client.get_or_create_collection(
            "topics",
            metadata=self.default_collection_metadata,
        )

    @staticmethod
    def format_topics_codes(topics: list[str]) -> dict[str, str]:
        """Return a dictionary of topics with their names in kebab case."""
        return {topic.lower().replace(" ", "-"): topic for topic in topics}

    @staticmethod
    def metadata_filter_none(
        metadata: dict[str, any], exclude: list[str] | None = None
    ) -> dict[str, any]:
        if exclude is None:
            exclude = []

        return {k: v for k, v in metadata.items() if v is not None and k not in exclude}

    def add(self, article: Document, summarization: ArticleSummarization) -> str:
        """Add an article and its summarization to the database."""
        metadata: ArticleMetadata = article.metadata
        url: str = metadata["url"]

        topics = self.format_topics_codes(summarization.topics)
        topics_ids: list[str] = list(topics.keys())
        topics_ids_str: str = ", ".join(topics_ids)

        document_metadata: dict[str, any] = self.metadata_filter_none(
            metadata, exclude=["url"]
        )
        document_metadata.update({"topics": topics_ids_str})

        self.articles.upsert(
            ids=[url],
            documents=[article.page_content],
            metadatas=[document_metadata],
        )

        self.summaries.upsert(
            ids=[url],
            documents=[summarization.summary],
            metadatas=[{"topics": topics_ids_str}],
        )

        self.topics.upsert(
            ids=topics_ids,
            documents=list(topics.values()),
        )

    def get_topics(self) -> dict[str, str]:
        topics_data = self.topics.get(include=["documents"])

        return {
            topic_id: topic_document
            for topic_id, topic_document in zip(
                topics_data["ids"], topics_data["documents"], strict=True
            )
        }

    def get_all(self) -> tuple[dict[str, str], list[Article]]:
        """Get all the topics and articles from the database."""
        topics = self.topics.get(include=["documents"])

        topics = {
            topic_id: topic_document
            for topic_id, topic_document in zip(
                topics["ids"], topics["documents"], strict=True
            )
        }

        articles = self.articles.get(include=["documents", "metadatas"])

        summaries = self.summaries.get(include=["documents"])

        articles_list: list[Article] = []
        for _id, article, metadata in zip(
            articles["ids"], articles["documents"], articles["metadatas"], strict=True
        ):
            topics_ids: list[str] = metadata.get("topics", "").split(", ")

            article_topics: list[str] = [
                topics.get(topic_id) for topic_id in topics_ids if topic_id in topics
            ]

            try:
                summary_index: int = summaries["ids"].index(_id)
                summary = summaries["documents"][summary_index]
            except ValueError:
                print(f"Unable to find summary for article {_id}")

            articles_list.append(
                Article(
                    url=_id, content=article, summary=summary, topics=article_topics
                )
            )

        return topics, articles_list

    def search(self, query: str) -> list[Article]:
        """Search for related articles based on vector distance. The threshold is configured in the settings."""
        topics = self.get_topics()

        articles_data = self.articles.query(
            query_texts=[query], include=["documents", "metadatas", "distances"]
        )

        articles_list: list[Article] = []
        for _id, content, metadata, distance in zip(
            articles_data["ids"][0],
            articles_data["documents"][0],
            articles_data["metadatas"][0],
            articles_data["distances"][0],
            strict=True,
        ):
            if distance > settings.search.articles_distance_threshold:
                print(f"Warning: [{_id}] Mark as not related. Distance: {distance:.2f}")
                continue

            topics_ids: list[str] = metadata.get("topics", "").split(", ")
            article_topics: list[str] = [
                topics.get(topic_id) for topic_id in topics_ids if topic_id in topics
            ]

            summaries_data = self.summaries.get(ids=[_id], include=["documents"])

            if not summaries_data["documents"]:
                print(f"[{_id}] Unable to find summary for the article")
                continue

            article = Article(
                url=_id,
                content=content,
                summary=summaries_data["documents"][0],
                topics=article_topics,
            )

            articles_list.append(article)

        if not articles_list:
            print(
                f"No related articles found for the query. Vector distance threshold: {settings.search.articles_distance_threshold:.2f}"
            )

        return articles_list
