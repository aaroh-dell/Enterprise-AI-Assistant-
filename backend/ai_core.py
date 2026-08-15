import os
import requests
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

load_dotenv()
BASE_URL = "http://127.0.0.1:8000"


# ============ STATE ============
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ============ TOOLS (bound to a specific logged-in employee) ============
def build_tools(employee_id: str):

    @tool
    def get_my_leave_balance() -> dict:
        """Fetch the logged-in employee's leave balance."""
        return requests.get(f"{BASE_URL}/leave/{employee_id}").json()

    @tool
    def get_my_info() -> dict:
        """Fetch the logged-in employee's name and department."""
        return requests.get(f"{BASE_URL}/employees/{employee_id}").json()

    @tool
    def create_ticket(issue: str) -> dict:
        """Create an IT support ticket for the logged-in employee."""
        return requests.post(f"{BASE_URL}/tickets", params={"employee_id": employee_id, "issue": issue}).json()

    @tool
    def submit_leave(start_date: str, end_date: str, reason: str) -> dict:
        """Submit a leave application for the logged-in employee."""
        return requests.post(f"{BASE_URL}/leave/apply", json={
            "employee_id": employee_id, "start_date": start_date, "end_date": end_date, "reason": reason
        }).json()

    @tool
    def get_holiday_calendar() -> dict:
        """Fetch the company holiday calendar."""
        return requests.get(f"{BASE_URL}/holidays").json()

    @tool
    def reset_my_password() -> dict:
        """Trigger a password reset for the logged-in employee's account."""
        return requests.post(f"{BASE_URL}/it/password-reset", params={"employee_id": employee_id}).json()

    @tool
    def check_ticket_status(ticket_id: int) -> dict:
        """Check the status of an IT support ticket by its ID."""
        return requests.get(f"{BASE_URL}/tickets/{ticket_id}").json()

    @tool
    def submit_expense(amount: float, category: str, description: str) -> dict:
        """Submit an expense reimbursement claim for the logged-in employee."""
        return requests.post(f"{BASE_URL}/expenses", json={
            "employee_id": employee_id, "amount": amount, "category": category, "description": description
        }).json()

    @tool
    def check_reimbursement_status(expense_id: int) -> dict:
        """Check the status of an expense reimbursement claim by its ID."""
        return requests.get(f"{BASE_URL}/expenses/{expense_id}").json()

    @tool
    def request_travel(destination: str, start_date: str, end_date: str, purpose: str) -> dict:
        """Submit a business travel request for the logged-in employee."""
        return requests.post(f"{BASE_URL}/travel", json={
            "employee_id": employee_id, "destination": destination,
            "start_date": start_date, "end_date": end_date, "purpose": purpose
        }).json()

    @tool
    def check_travel_status(travel_id: int) -> dict:
        """Check the status of a travel request by its ID."""
        return requests.get(f"{BASE_URL}/travel/{travel_id}").json()

    @tool
    def estimate_travel_budget(destination: str, days: int) -> dict:
        """Estimate the travel budget for a trip based on destination and number of days."""
        return requests.get(f"{BASE_URL}/travel/budget/estimate", params={"destination": destination, "days": days}).json()

    return [
        get_my_leave_balance, get_my_info, create_ticket, submit_leave,
        get_holiday_calendar, reset_my_password, check_ticket_status,
        submit_expense, check_reimbursement_status,
        request_travel, check_travel_status, estimate_travel_budget,
    ]


SYSTEM_PROMPT = """
You are EnterpriseAssist, an internal AI assistant for company employees.
You are already talking to a verified, logged-in employee - their identity
is handled automatically, you never need to ask for their employee ID.

SCOPE:
- You help with HR (leave, policies), IT (tickets, password resets),
  Finance (expenses), and Travel requests.
- You do NOT answer questions unrelated to company/work matters.
  If asked something out of scope, politely say it's outside what you help with.

BEHAVIOR RULES:
- Always confirm key details (dates, amounts, reasons) before submitting anything.
- Keep responses short and professional - 2 to 4 sentences unless more detail is requested.
- Never invent data - always use tools for real information or actions.
- If a tool call fails, say so honestly.
"""


def build_graph(employee_id: str):
    """Builds a fresh graph bound to this employee's tools."""
    tools = build_tools(employee_id)

    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: State):
        messages = state["messages"]
        # Inject the system prompt at the start of every call, without
        # permanently storing it inside the saved message history
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot_node)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")

    return graph_builder.compile()


def get_ai_response(chat_history, user_input, employee_id):
    """
    chat_history: a plain list of LangGraph messages (kept in Streamlit's session_state)
    Returns the AI's text reply, and mutates chat_history in place with the new turns.
    """
    graph = build_graph(employee_id)

    chat_history.append({"role": "user", "content": user_input})
    result = graph.invoke({"messages": chat_history})

    reply = result["messages"][-1]
    if isinstance(reply.content, str):
        text = reply.content
    else:
        text = "".join(block.get("text", "") for block in reply.content if isinstance(block, dict))

    # Replace the caller's history with the full updated conversation
    chat_history.clear()
    chat_history.extend(result["messages"])

    return text