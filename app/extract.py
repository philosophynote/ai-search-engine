"""
The extract node is responsible for extracting information from a tavily search.
"""

import json

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from app.state import AgentState
from app.model import get_model


async def extract_node(state: AgentState, config: RunnableConfig):
    """
    The extract node is responsible for extracting information from a tavily search.
    """

    current_step = next(
        (step for step in state["steps"] if step["status"] == "pending"), None
    )

    if current_step is None:
        raise ValueError("No current step")

    if current_step["type"] != "search":
        raise ValueError("Current step is not of type search")

    system_message = f"""
This step was just executed: {json.dumps(current_step)}

NOTE: When generating the output, ensure that the 'capital' and 'number_of_employees' fields conform to the CompanyInfo type definition (i.e. they must be integers).

The search has returned a set of results related to corporate information.

Please summarize ONLY the search results and return the summary in the JSON format described in the README.
The JSON response must include the following keys:
- company_name, furigana, corporate_number, location, representative_name, officer_names, company_url, service_url, industry, establishment_date, capital, number_of_employees, phone_number, source_urls

For the "industry" key, ensure the answer is always chosen from the names provided in industry.md.
Do not include any extra information.
Format the answer strictly as JSON.
"""

    response = await get_model(state).ainvoke(
        [state["messages"][0], HumanMessage(content=system_message)], config
    )

    current_step["result"] = response.content
    current_step["search_result"] = None
    current_step["status"] = "complete"
    current_step["updates"] = [*current_step["updates"], "Done."]

    next_step = next(
        (step for step in state["steps"] if step["status"] == "pending"), None
    )
    if next_step:
        next_step["updates"] = ["Searching the web..."]

    return state
