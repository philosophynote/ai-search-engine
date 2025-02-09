"""
The search node is responsible for searching the internet for information.
"""

import json
from datetime import datetime
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_community.tools import TavilySearchResults
from app.state import AgentState
from app.model import get_model


async def search_node(state: AgentState, config: RunnableConfig):
    """
    The search node is responsible for searching the internet for information.
    """
    tavily_tool = TavilySearchResults(
        max_results=10,  # Max search results to return
        search_depth="advanced",  # The depth of the search. It can be “basic” or “advanced”
        include_answer=True,  # Include a short answer to original query in the search results.
        include_raw_content=True,  # Include cleaned and parsed HTML of each site search results.
        include_images=True,  # Include a list of query related images in the response.
    )

    current_step = next(
        (step for step in state["steps"] if step["status"] == "pending"), None
    )

    if current_step is None:
        raise ValueError("No step to search for")

    if current_step["type"] != "search":
        raise ValueError("Current step is not a search step")

    instructions = f"""
This is a step in a series of steps aimed at retrieving detailed corporate information.
These are all of the steps: {json.dumps(state["steps"])}

You are responsible for executing the following search step: {json.dumps(current_step)}
The current date is {datetime.now().strftime("%Y-%m-%d")}.
Please generate an effective search query to find corporate details relevant to the following description:
{current_step["description"]}
Ensure that the search query is optimized for retrieving corporate information.
"""
    model = get_model(state).bind_tools([tavily_tool], tool_choice=tavily_tool.name)

    response = await model.ainvoke([HumanMessage(content=instructions)], config)

    tool_msg = tavily_tool.invoke(response.tool_calls[0])

    current_step["search_result"] = json.loads(tool_msg.content)
    current_step["updates"] = [*current_step["updates"], "Extracting information..."]
    return state
