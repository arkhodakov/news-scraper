from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class ArticleSummarization(BaseModel):
    summary: str = Field(
        description="A concise summary of the article that captures its main points and key information."
    )
    topics: list[str] = Field(
        description="The main topics discussed in the article. These should be broad categories or themes that encompass the article's content."
    )


ArticleSummarySchema: str = PydanticOutputParser(
    pydantic_object=ArticleSummarization
).get_output_jsonschema()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                You are tasked with summarizing a news article and identifying its main topics.
                This information will be used to create a structured representation of the article's content.

                Please follow these steps:
                1. Carefully read and analyze the entire article.
                2. Create a concise summary of the article that captures its main points and key information.
                3. Identify main topics discussed in the article. These should be broad categories or themes that encompass the article's content.

                Here's an example of what your output should look like:
                <example>
                {{
                "summary": "SpaceX successfully launched its Starship rocket for a test flight, reaching an altitude of 150 km before an unexpected explosion. Despite the setback, CEO Elon Musk praised the mission as a significant step forward in space exploration technology.",
                "topics": ["Space Technology", "Rocket Launch", "SpaceX", "Aerospace Industry"]
                }}
                </example>

                Important considerations:
                - Ensure your summary is objective and factual, avoiding any personal opinions or biases.
                - Topics should be general enough to be applicable across different articles but specific enough to be meaningful for this particular piece.
                - Do not include any information in the summary or topics that is not present in the original article.
                - Aim for clarity and conciseness in both the summary and topic selection.

                Please provide your output in the following JSON schema:
                <schema>
                {schema}
                </schema>

                Do not include anything else except the JSON object.
            """,
        ),
        (
            "user",
            """
                The article content to summarize:
                <content>
                {content}
                </content>
            """,
        ),
    ]
)


async def summarize(document: Document, model: BaseChatModel) -> ArticleSummarization:
    response = await model.ainvoke(
        prompt.invoke(
            {"content": document.page_content, "schema": ArticleSummarySchema}
        )
    )

    summary = ArticleSummarization.model_validate_json(response.content)

    return summary
