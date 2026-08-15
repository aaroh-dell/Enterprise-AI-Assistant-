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

IT_SYSTEM_PROMPT = """
You are the IT specialist for EnterpriseAssist. You handle IT support tickets,
ticket status checks, and password resets. Stay focused on these topics only.
Confirm the issue clearly before creating a ticket.
"""


class ITState(TypedDict):
    messages: Annotated[list, add_messages]


def build_it_tools(employee_id: str):
    @tool
    def create_ticket(issue: str) -> dict:
        """Create an IT support ticket for the logged-in employee."""
        return call_with_retry(lambda: requests.post(
            f"{BASE_URL}/tickets", params={"employee_id": employee_id, "issue": issue}
        ).json())

    @tool
    def check_ticket_status(ticket_id: int) -> dict:
        """Check the status of an IT support ticket by its ID."""
        return call_with_retry(lambda: requests.get(f"{BASE_URL}/tickets/{ticket_id}").json())

    @tool
    def reset_my_password() -> dict:
        """Trigger a password reset for the logged-in employee's account."""
        return call_with_retry(lambda: requests.post(
            f"{BASE_URL}/it/password-reset", params={"employee_id": employee_id}
        ).json())

    return [create_ticket, check_ticket_status, reset_my_password]


def route_after_it(state: ITState, sensitive_tools: set):
    last_message = state["messages"][-1]
    if not getattr(last_message, "tool_calls", None):
        return END
    for call in last_message.tool_calls:
        if call["name"] in sensitive_tools:
            return END
    return "tools"


def build_it_graph(employee_id: str, sensitive_tools: set):
    tools = build_it_tools(employee_id)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    def it_node(state: ITState):
        full_messages = [{"role": "system", "content": IT_SYSTEM_PROMPT}] + state["messages"]
        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(ITState)
    graph.add_node("it", it_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "it")
    graph.add_conditional_edges("it", lambda s: route_after_it(s, sensitive_tools))
    graph.add_edge("tools", "it")

    return graph.compile(), tools