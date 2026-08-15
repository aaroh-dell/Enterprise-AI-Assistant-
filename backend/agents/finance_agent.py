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

FINANCE_SYSTEM_PROMPT = """
You are the Finance specialist for EnterpriseAssist. You handle expense
reimbursement submissions and reimbursement status checks. Stay focused on
these topics only. Confirm the amount, category, and description before submitting.
"""


class FinanceState(TypedDict):
    messages: Annotated[list, add_messages]


def build_finance_tools(employee_id: str):
    @tool
    def submit_expense(amount: float, category: str, description: str) -> dict:
        """Submit an expense reimbursement claim for the logged-in employee."""
        return call_with_retry(lambda: requests.post(f"{BASE_URL}/expenses", json={
            "employee_id": employee_id, "amount": amount, "category": category, "description": description
        }).json())

    @tool
    def check_reimbursement_status(expense_id: int) -> dict:
        """Check the status of an expense reimbursement claim by its ID."""
        return call_with_retry(lambda: requests.get(f"{BASE_URL}/expenses/{expense_id}").json())

    return [submit_expense, check_reimbursement_status]


def route_after_finance(state: FinanceState, sensitive_tools: set):
    last_message = state["messages"][-1]
    if not getattr(last_message, "tool_calls", None):
        return END
    for call in last_message.tool_calls:
        if call["name"] in sensitive_tools:
            return END
    return "tools"


def build_finance_graph(employee_id: str, sensitive_tools: set):
    tools = build_finance_tools(employee_id)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    def finance_node(state: FinanceState):
        full_messages = [{"role": "system", "content": FINANCE_SYSTEM_PROMPT}] + state["messages"]
        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(FinanceState)
    graph.add_node("finance", finance_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "finance")
    graph.add_conditional_edges("finance", lambda s: route_after_finance(s, sensitive_tools))
    graph.add_edge("tools", "finance")

    return graph.compile(), tools