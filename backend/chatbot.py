import os
import requests  # NEW (Step 4): lets Python make HTTP calls to your backend
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================================
# NEW (Step 4): The tool function itself.
# This is plain Python — it calls your Phase 4 backend over HTTP,
# exactly like your browser did when you visited /leave/101.
# ============================================================
def get_leave_balance(employee_id: str):
    """Fetch an employee's real leave balance from the backend API."""
    response = requests.get(f"http://127.0.0.1:8000/leave/{employee_id}")
    return response.json()

def get_employee_info(employee_id: str):
    """Fetch an employee's name and department from the backend API."""
    response = requests.get(f"http://127.0.0.1:8000/employees/{employee_id}")
    return response.json()


def create_ticket(employee_id: str, issue: str):
    """Create a new IT support ticket for an employee and return the ticket details."""
    response = requests.post(
        "http://127.0.0.1:8000/tickets",
        params={"employee_id": employee_id, "issue": issue},
    )
    return response.json()

def submit_leave(employee_id: str, start_date: str, end_date: str, reason: str):
    """Submit a leave application for an employee with start date, end date, and reason."""
    response = requests.post(
        "http://127.0.0.1:8000/leave/apply",
        json={
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
        },
    )
    return response.json()


def get_holiday_calendar():
    """Fetch the company holiday calendar."""
    response = requests.get("http://127.0.0.1:8000/holidays")
    return response.json()

def reset_password(employee_id: str):
    """Trigger a password reset for an employee's account."""
    response = requests.post(
        "http://127.0.0.1:8000/it/password-reset",
        params={"employee_id": employee_id},
    )
    return response.json()


def check_ticket_status(ticket_id: int):
    """Check the status of an existing IT support ticket by its ID."""
    response = requests.get(f"http://127.0.0.1:8000/tickets/{ticket_id}")
    return response.json()

# NOTE: I also updated the guardrail text below, since the old version
# told the AI it has NO access to real data - that's no longer true now
# that we're giving it a tool. Leaving the old wording in would confuse
# the model into refusing even when it CAN look things up.
SYSTEM_PROMPT = """
You are EnterpriseAssist, an internal AI assistant for company employees.

SCOPE:
- You help with HR (leave, policies), IT (tickets, password resets),
  Finance (expenses), and Travel requests.
- You do NOT answer questions unrelated to company/work matters
  (e.g. general trivia, personal advice, coding help for personal projects).
  If asked something out of scope, politely say it's outside what you help with.

BEHAVIOR RULES:
- Always confirm key details (dates, amounts, reasons) before saying you'll submit anything.
- Keep responses short and professional - 2 to 4 sentences unless more detail is requested.
- You have tools to check an employee's real leave balance, look up employee info,
  and create IT support tickets. Use them whenever a request needs real data or
  a real action - do not guess or claim something is done if you haven't called the tool.
- Before creating a ticket, confirm the employee ID and a clear description of the issue.
- If a tool call fails or the employee isn't found, say so honestly.

EXAMPLES:

User: I need 3 days off next week.
EnterpriseAssist: I can help with that. Could you confirm the exact dates and the reason (personal, medical, or other)?

User: What's the capital of France?
EnterpriseAssist: That's outside what I help with here — I'm focused on HR, IT, Finance, and Travel matters for employees.
"""

# ============================================================
# NEW (Step 5): Give the model the list of tools it's allowed to use.
# This is just a list containing the function itself - not calling it,
# just handing the AI the *capability*.
# ============================================================
tools = [get_leave_balance, get_employee_info, create_ticket, submit_leave, get_holiday_calendar, reset_password, check_ticket_status]

chat_history = []

print("EnterpriseAssist v3 (with tool calling) — type 'exit' to quit\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    chat_history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=chat_history,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=tools,  # NEW (Step 6): this line is what turns tool calling on
        ),
    )

    print(f"AI: {response.text}\n")

    chat_history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))

