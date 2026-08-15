import os
import requests
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from backend.retry_utils import call_with_retry
from backend.config import BASE_URL

TRAVEL_SYSTEM_PROMPT = """
You are the Travel specialist for EnterpriseAssist. You handle business travel
requests, travel status checks, and budget estimates. Stay focused on these
topics only. Confirm destination and dates before submitting a travel request.
"""


class TravelState(TypedDict):
    messages: Annotated[list, add_messages]


def build_travel_tools(employee_id: str):
    @tool
    def request_travel(destination: str, start_date: str, end_date: str, purpose: str) -> dict:
        """Submit a business travel request for the logged-in employee."""
        return call_with_retry(lambda: requests.post(f"{BASE_URL}/travel", json={
            "employee_id": employee_id, "destination": destination,
            "start_date": start_date, "end_date": end_date, "purpose": purpose
        }).json())

    @tool
    def check_travel_status(travel_id: int) -> dict:
        """Check the status of a travel request by its ID."""
        return call_with_retry(lambda: requests.get(f"{BASE_URL}/travel/{travel_id}").json())

    @tool
    def estimate_travel_budget(destination: str, days: int) -> dict:
        """Estimate the travel budget for a trip based on destination and number of days."""
        return call_with_retry(lambda: requests.get(
            f"{BASE_URL}/travel/budget/estimate", params={"destination": destination, "days": days}
        ).json())

    return [request_travel, check_travel_status, estimate_travel_budget]


def route_after_travel(state: TravelState, sensitive_tools: set):
    last_message = state["messages"][-1]
    if not getattr(last_message, "tool_calls", None):
        return END
    for call in last_message.tool_calls:
        if call["name"] in sensitive_tools:
            return END
    return "tools"


def build_travel_graph(employee_id: str, sensitive_tools: set):
    tools = build_travel_tools(employee_id)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    def travel_node(state: TravelState):
        full_messages = [{"role": "system", "content": TRAVEL_SYSTEM_PROMPT}] + state["messages"]
        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(TravelState)
    graph.add_node("travel", travel_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "travel")
    graph.add_conditional_edges("travel", lambda s: route_after_travel(s, sensitive_tools))
    graph.add_edge("tools", "travel")

    return graph.compile(), tools