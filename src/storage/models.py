from pydantic import BaseModel


class Article(BaseModel):
    """A model to describe an article and all its data that is stored in the database."""

    url: str
    content: str
    summary: str
    topics: list[str]

    @property
    def id(self) -> str:
        return self.url

    def __str__(self) -> str:
        return (
            f"[{self.url}]\nSummary: {self.summary}\nTopics: {', '.join(self.topics)}"
        )
