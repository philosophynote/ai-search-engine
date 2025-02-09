"""
This node is responsible for creating the steps for the research process.
"""

# pylint: disable=line-too-long

from typing import List
from datetime import datetime
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool

from pydantic import BaseModel, Field
from app.state import AgentState
from app.model import get_model
# 新しい CompanyInfo を import
from app.types.companyinfo import CompanyInfo


class SearchStep(BaseModel):
    """Model for a search step"""

    id: str = Field(
        description="The id of the step. This is used to identify the step in the state. Just make sure it is unique."
    )
    description: str = Field(
        description='The description of the step, i.e. "search for information about the latest AI news"'
    )
    status: str = Field(
        description='The status of the step. Always "pending".', enum=["pending"]
    )
    type: str = Field(description="The type of step.", enum=["search"])


# https://zenn.dev/pharmax/articles/1b351b730eef61
@tool
def SearchTool(steps: List[SearchStep]):  # pylint: disable=invalid-name,unused-argument
    """
    Break the user's query into smaller steps.
    Use step type "search" to search the web for information.
    Make sure to add all the steps needed to answer the user's query.
    """


async def steps_node(state: AgentState, config: RunnableConfig):
    """
    The steps node is responsible for building the steps in the research process.
    """
    # 調査対象を制限するため、CompanyInfo のキーのみを対象とする旨を追記
    corporate_keys = ", ".join([
        "company_name", "furigana", "corporate_number", "location",
        "representative_name", "officer_names", "company_url", "service_url",
        "industry", "establishment_date", "capital", "number_of_employees",
        "phone_number", "source_urls"
    ])
    instructions = f"""
You are a corporate information search assistant.
Your task is to help the user with complex queries regarding corporate details by breaking them down into smaller steps.
Each step should contribute to finding information limited to the following keys: {corporate_keys}.
Do not search for unrelated or extraneous information.
The current date is {datetime.now().strftime("%Y-%m-%d")}.
"""

    response = (
        await get_model(state)
        .bind_tools(
            [SearchTool], tool_choice="SearchTool"
        )  # bind_toolはLangchainの関数で、使用可能なツールを指定する、tool_choiceはツールを指定する
        .ainvoke(
            [
                state["messages"][0],
                HumanMessage(content=instructions),
            ],
        )
    )

    if len(response.tool_calls) == 0:
        steps = []
    else:
        steps = response.tool_calls[0]["args"]["steps"]

    if len(steps) != 0:
        steps[0]["updates"] = ["Searching the web..."]

    return {
        "steps": steps,
    }
