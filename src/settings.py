from typing import Tuple, Type

from chromadb.config import DEFAULT_DATABASE, DEFAULT_TENANT
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class StorageSettings(BaseModel):
    """Configure the behavior and the location of the database."""

    path: str = Field(
        default="./data",
        help="The path to the directory where the database data will be stored",
    )
    tenant: str = Field(
        default=DEFAULT_TENANT, help="The tenant to use for the database"
    )
    database: str = Field(
        default=DEFAULT_DATABASE, help="The name of the database to use"
    )


class SearchSettings(BaseModel):
    """Configure how the semantic search will be performed."""

    topics_distance_threshold: float = Field(
        default=0.3,
        help="The cosine distance threshold to match the search query with a topic",
        ge=0,
        le=1,
    )
    topics_search: bool = Field(
        default=True,
        help="Whether to enable topic-based search. It will return all articles that have a related topic",
    )

    summaries_distance_threshold: float = Field(
        default=0.3,
        help="The cosine distance threshold to match the search query with a summary",
        ge=0,
        le=1,
    )
    summaries_search: bool = Field(
        default=True,
        help="Whether to enable summary-based search. It will return all articles that have a related summary",
    )

    articles_distance_threshold: float = Field(
        default=0.3,
        help="The cosine distance threshold to match the search query with an article",
        ge=0,
        le=1,
    )


class LLMSettings(BaseModel):
    """Configure the provider and the default model to use for LLM related tasks.

    OpenAI is the default choice, but other providers that support OpenAI API are welcome as well.
    """

    base_url: str = Field(
        default="https://api.openai.com/v1",
        help="The base OpenAI compatible API URL. Can be use to configure local LLM inference server.",
    )
    model: str = Field(default="gpt-4o-mini", help="The model to use for LLM tasks.")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")

    storage: StorageSettings = Field(default_factory=StorageSettings)

    search: SearchSettings = Field(default_factory=SearchSettings)

    llm: LLMSettings = Field(default_factory=LLMSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


settings = Settings()
