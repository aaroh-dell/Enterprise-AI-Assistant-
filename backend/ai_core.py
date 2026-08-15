import os
import requests
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

load_dotenv()
BASE_URL = "http://127.0.0.1:8000"

SENSITIVE_TOOLS = {"submit_leave", "create_ticket", "submit_expense", "request_travel"}


class State(TypedDict):
    messages: Annotated[list, add_messages]


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
- Keep responses short and professional - 2 to 4 sentences unless more detail is requested.
- Never invent data - always use tools for real information or actions.
- If a tool call fails, say so honestly.
- Submitting leave, creating tickets, submitting expenses, and requesting travel
  are handled with a separate confirmation step automatically - just call the
  tool when you have enough information, you don't need to ask "shall I submit?" yourself.
"""


def route_after_chatbot(state: State):
    last_message = state["messages"][-1]
    if not getattr(last_message, "tool_calls", None):
        return END
    for call in last_message.tool_calls:
        if call["name"] in SENSITIVE_TOOLS:
            return END
    return "tools"


def build_graph(tools):
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: State):
        messages = state["messages"]
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot_node)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", route_after_chatbot)
    graph_builder.add_edge("tools", "chatbot")

    return graph_builder.compile()


def _extract_text(message):
    if isinstance(message.content, str):
        return message.content
    return "".join(block.get("text", "") for block in message.content if isinstance(block, dict))


def _describe_action(tool_name: str, args: dict) -> str:
    descriptions = {
        "submit_leave": f"submit leave from {args.get('start_date')} to {args.get('end_date')} ({args.get('reason')})",
        "create_ticket": f"create an IT ticket: \"{args.get('issue')}\"",
        "submit_expense": f"submit a ₹{args.get('amount')} expense under {args.get('category')} ({args.get('description')})",
        "request_travel": f"request travel to {args.get('destination')} from {args.get('start_date')} to {args.get('end_date')}",
    }
    return descriptions.get(tool_name, f"run {tool_name}")


def get_ai_response(chat_history, user_input, employee_id, pending_action=None):
    """
    Returns (reply_text, new_pending_action).
    """
    tools = build_tools(employee_id)
    tool_lookup = {t.name: t for t in tools}

    # ---------- CASE 1: waiting on a confirmation ----------
    if pending_action:
        decision = user_input.strip().lower()

        if decision in ("yes", "y", "confirm", "yes please", "go ahead", "do it"):
            tool_obj = tool_lookup[pending_action["tool_name"]]
            result_data = tool_obj.invoke(pending_action["tool_args"])

            chat_history.append(
                ToolMessage(
                    content=str(result_data),
                    tool_call_id=pending_action["tool_call_id"],
                    name=pending_action["tool_name"],
                )
            )

            # Reuse the same tool-bound graph used for normal turns instead
            # of a separate bare LLM call - fixes the "prefilling" error,
            # since Gemini validates tool-response messages against the
            # tool declarations present in THAT specific request.
            graph = build_graph(tools)
            result = graph.invoke({"messages": chat_history})

            chat_history.clear()
            chat_history.extend(result["messages"])

            return _extract_text(chat_history[-1]), None

        elif decision in ("no", "n", "cancel", "nevermind", "stop"):
            # Must resolve the pending tool call with a real ToolMessage,
            # even on cancellation - otherwise the NEXT turn hits the same
            # unresolved-tool-call error.
            chat_history.append(
                ToolMessage(
                    content="Cancelled by the user - action was not performed.",
                    tool_call_id=pending_action["tool_call_id"],
                    name=pending_action["tool_name"],
                )
            )
            cancel_text = "Okay, I've cancelled that - nothing was submitted."
            chat_history.append({"role": "assistant", "content": cancel_text})
            return cancel_text, None

        else:
            return "Please reply 'yes' to confirm or 'no' to cancel.", pending_action

    # ---------- CASE 2: normal turn ----------
    chat_history.append({"role": "user", "content": user_input})
    graph = build_graph(tools)
    result = graph.invoke({"messages": chat_history})

    chat_history.clear()
    chat_history.extend(result["messages"])

    last_message = chat_history[-1]

    if getattr(last_message, "tool_calls", None):
        for call in last_message.tool_calls:
            if call["name"] in SENSITIVE_TOOLS:
                new_pending = {
                    "tool_name": call["name"],
                    "tool_args": call["args"],
                    "tool_call_id": call["id"],
                }
                question = f"You're about to {_describe_action(call['name'], call['args'])}. Confirm? (yes/no)"
                # Deliberately NOT appended to chat_history - the model-facing
                # history must end with the tool-call request until a real
                # ToolMessage resolves it. The UI shows this via the return value only.
                return question, new_pending

    return _extract_text(last_message), None