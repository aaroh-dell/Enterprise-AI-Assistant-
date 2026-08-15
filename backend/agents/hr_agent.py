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

HR_SYSTEM_PROMPT = """
You are the HR specialist for EnterpriseAssist. You handle leave balances,
leave applications, holidays, and employee info lookups. Stay focused on
these topics only. Confirm details before submitting leave.
"""


class HRState(TypedDict):
    messages: Annotated[list, add_messages]


def build_hr_tools(employee_id: str):
    @tool
    def get_my_leave_balance() -> dict:
        """Fetch the logged-in employee's leave balance."""
        return call_with_retry(lambda: requests.get(f"{BASE_URL}/leave/{employee_id}").json())

    @tool
    def submit_leave(start_date: str, end_date: str, reason: str) -> dict:
        """Submit a leave application for the logged-in employee."""
        return call_with_retry(lambda: requests.post(f"{BASE_URL}/leave/apply", json={
            "employee_id": employee_id, "start_date": start_date, "end_date": end_date, "reason": reason
        }).json())

    @tool
    def get_holiday_calendar() -> dict:
        """Fetch the company holiday calendar."""
        return call_with_retry(lambda: requests.get(f"{BASE_URL}/holidays").json())

    @tool
    def get_my_info() -> dict:
        """Fetch the logged-in employee's name and department."""
        return call_with_retry(lambda: requests.get(f"{BASE_URL}/employees/{employee_id}").json())

    return [get_my_leave_balance, submit_leave, get_holiday_calendar, get_my_info]


def route_after_hr(state: HRState, sensitive_tools: set):
    last_message = state["messages"][-1]
    if not getattr(last_message, "tool_calls", None):
        return END
    for call in last_message.tool_calls:
        if call["name"] in sensitive_tools:
            return END
    return "tools"


def build_hr_graph(employee_id: str, sensitive_tools: set):
    tools = build_hr_tools(employee_id)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    def hr_node(state: HRState):
        full_messages = [{"role": "system", "content": HR_SYSTEM_PROMPT}] + state["messages"]
        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(HRState)
    graph.add_node("hr", hr_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "hr")
    graph.add_conditional_edges("hr", lambda s: route_after_hr(s, sensitive_tools))
    graph.add_edge("tools", "hr")

    return graph.compile(), tools