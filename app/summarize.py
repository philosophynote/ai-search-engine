"""
The summarize node is responsible for summarizing the information.
"""

import json
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool

from pydantic import BaseModel, Field
from app.state import AgentState
from app.model import get_model


class Reference(BaseModel):
    """Model for a reference"""

    title: str = Field(description="The title of the reference.")
    url: str = Field(description="The url of the reference.")


class SummarizeInput(BaseModel):
    """Input for the summarize tool"""

    markdown: str = Field(
        description="""
                          The markdown formatted summary of the final result.
                          If you add any headings, make sure to start at the top level (#).
                          """
    )
    references: list[Reference] = Field(description="A list of references.")


# 最終結果を要約する。要約が完全であることを確認し
# すべての関連情報と参照リンクが含まれていることを確認する。
@tool(args_schema=SummarizeInput)
def SummarizeTool(summary: str, references: list[Reference]):  # pylint: disable=invalid-name,unused-argument
    """
    Summarize the final result. Make sure that the summary is complete and
    includes all relevant information and reference links.
    """


async def summarize_node(state: AgentState, config: RunnableConfig):
    """
    The summarize node is responsible for summarizing the information.
    """
    system_message = f"""
The system has performed a series of steps to answer the user's query.
These are all of the steps: {json.dumps(state["steps"])}

Please summarize the final result and include all relevant information and reference links.
"""

    response = (
        await get_model(state)
        .bind_tools([SummarizeTool], tool_choice="SummarizeTool")
        .ainvoke(
            [
                HumanMessage(content=system_message),
            ],
        )
    )

    return {
        "answer": response.tool_calls[0]["args"],
    }
