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
from app.types.companyinfo import CompanyInfo

async def summarize_node(state: AgentState, config: RunnableConfig):
    """
    The summarize node is responsible for summarizing the information.
    """
    system_message = f"""
The system has performed a series of steps to answer the user's query regarding corporate information.
These are all of the steps: {json.dumps(state["steps"])}

Please summarize the final result and return the answer strictly in the under JSON format.
The JSON object must include:
- company_name
- furigana
- corporate_number
- location
- representative_name
- officer_names
- company_url
- service_url
- industry
- establishment_date
- capital
- number_of_employees(answer in number format)
- phone_number
- source_urls

Do not include any extra information.
"""
    response = (
        await get_model(state)
        .with_structured_output(CompanyInfo, method="json_mode")
        .ainvoke(
            [
                HumanMessage(content=system_message),
            ],
        )
    )
    print("state:")
    print(state)
    print("response:")
    print(response)
    # CompanyInfo 型のデータを JSON 形式で返却
    return response
