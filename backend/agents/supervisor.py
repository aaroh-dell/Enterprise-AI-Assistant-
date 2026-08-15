import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage

from backend.agents.hr_agent import build_hr_graph
from backend.agents.it_agent import build_it_graph
from backend.agents.finance_agent import build_finance_graph
from backend.agents.travel_agent import build_travel_graph
from backend.agents.knowledge_agent import build_knowledge_graph

load_dotenv()

SENSITIVE_TOOLS = {"submit_leave", "create_ticket", "submit_expense", "request_travel"}

ROUTER_PROMPT = """
You are a routing classifier for EnterpriseAssist, an internal company assistant.
Read the employee's message and decide which single department should handle it.

Departments:
- HR: leave balance, leave applications, holidays, employee info
- IT: IT support tickets, ticket status, password resets
- FINANCE: expense submissions, reimbursement status
- TRAVEL: business travel requests, travel status, travel budget estimates
- KNOWLEDGE: questions about company policies (leave policy text, benefits, IT/security policies, finance policies)
- OFF_TOPIC: anything unrelated to company HR/IT/Finance/Travel/policy matters

Respond with EXACTLY ONE WORD from: HR, IT, FINANCE, TRAVEL, KNOWLEDGE, OFF_TOPIC
No punctuation, no explanation - just the single word.
"""

_router_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", api_key=os.getenv("GEMINI_API_KEY"))


def _classify(user_input: str) -> str:
    response = _router_llm.invoke([
        {"role": "system", "content": ROUTER_PROMPT},
        {"role": "user", "content": user_input},
    ])

    if isinstance(response.content, str):
        text = response.content
    else:
        text = "".join(
            block.get("text", "") for block in response.content if isinstance(block, dict)
        )

    decision = text.strip().upper()

    valid = {"HR", "IT", "FINANCE", "TRAVEL", "KNOWLEDGE", "OFF_TOPIC"}
    return decision if decision in valid else "OFF_TOPIC"


def _extract_text(message):
    if isinstance(message.content, str):
        return message.content
    return "".join(block.get("text", "") for block in message.content if isinstance(block, dict))


def route_and_respond(chat_history, user_input, employee_id, pending_action=None):
    """
    Supervisor entrypoint - decides which specialist handles the message,
    then delegates to it. Returns (reply_text, new_pending_action).
    """

    # ---------- CASE 1: waiting on a confirmation from a PREVIOUS specialist turn ----------
    if pending_action:
        department = pending_action["department"]
        tools, tool_lookup = _get_tools_for_department(department, employee_id)

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

            graph, _ = _build_graph_for_department(department, employee_id)
            result = graph.invoke({"messages": chat_history})
            chat_history.clear()
            chat_history.extend(result["messages"])
            return _extract_text(chat_history[-1]), None

        elif decision in ("no", "n", "cancel", "nevermind", "stop"):
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

    # ---------- CASE 2: normal turn - classify and delegate ----------
    department = _classify(user_input)

    if department == "OFF_TOPIC":
        reply = "That's outside what I help with here - I'm focused on HR, IT, Finance, Travel, and company policy matters for employees."
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": reply})
        return reply, None

    chat_history.append({"role": "user", "content": user_input})
    graph, tools = _build_graph_for_department(department, employee_id)
    result = graph.invoke({"messages": chat_history})

    chat_history.clear()
    chat_history.extend(result["messages"])

    last_message = chat_history[-1]

    if getattr(last_message, "tool_calls", None):
        for call in last_message.tool_calls:
            if call["name"] in SENSITIVE_TOOLS:
                new_pending = {
                    "department": department,
                    "tool_name": call["name"],
                    "tool_args": call["args"],
                    "tool_call_id": call["id"],
                }
                question = f"You're about to {_describe_action(call['name'], call['args'])}. Confirm? (yes/no)"
                return question, new_pending

    return _extract_text(last_message), None


def _build_graph_for_department(department: str, employee_id: str):
    if department == "HR":
        return build_hr_graph(employee_id, SENSITIVE_TOOLS)
    if department == "IT":
        return build_it_graph(employee_id, SENSITIVE_TOOLS)
    if department == "FINANCE":
        return build_finance_graph(employee_id, SENSITIVE_TOOLS)
    if department == "TRAVEL":
        return build_travel_graph(employee_id, SENSITIVE_TOOLS)
    if department == "KNOWLEDGE":
        return build_knowledge_graph()
    raise ValueError(f"Unknown department: {department}")


def _get_tools_for_department(department: str, employee_id: str):
    _, tools = _build_graph_for_department(department, employee_id)
    return tools, {t.name: t for t in tools}


def _describe_action(tool_name: str, args: dict) -> str:
    descriptions = {
        "submit_leave": f"submit leave from {args.get('start_date')} to {args.get('end_date')} ({args.get('reason')})",
        "create_ticket": f"create an IT ticket: \"{args.get('issue')}\"",
        "submit_expense": f"submit a ₹{args.get('amount')} expense under {args.get('category')} ({args.get('description')})",
        "request_travel": f"request travel to {args.get('destination')} from {args.get('start_date')} to {args.get('end_date')}",
    }
    return descriptions.get(tool_name, f"run {tool_name}")