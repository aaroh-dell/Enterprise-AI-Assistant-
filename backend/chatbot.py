import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Session identity - set once at login, used by every tool call after
current_employee_id = None

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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


def submit_expense(employee_id: str, amount: float, category: str, description: str):
    """Submit an expense reimbursement claim for an employee."""
    response = requests.post(
        "http://127.0.0.1:8000/expenses",
        json={
            "employee_id": employee_id,
            "amount": amount,
            "category": category,
            "description": description,
        },
    )
    return response.json()


def check_reimbursement_status(expense_id: int):
    """Check the status of a submitted expense reimbursement claim by its ID."""
    response = requests.get(f"http://127.0.0.1:8000/expenses/{expense_id}")
    return response.json()


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
  create IT support tickets, submit leave, check holidays, reset passwords, check
  ticket status, submit expenses, and check reimbursement status. Use them whenever
  a request needs real data or a real action - do not guess or claim something is
  done if you haven't called the tool.
- Before creating a ticket, submitting leave, or submitting an expense, confirm the
  relevant details first.
- If a tool call fails or the employee isn't found, say so honestly.
"""

tools = [
    get_leave_balance, get_employee_info, create_ticket,
    submit_leave, get_holiday_calendar,
    reset_password, check_ticket_status,
    submit_expense, check_reimbursement_status,
]

# ============================================================
# LOGIN - runs once at startup, before the chat loop begins
# ============================================================
print("=== EnterpriseAssist Login ===")
login_id = input("Employee ID: ")
login_password = input("Password: ")

login_response = requests.post(
    "http://127.0.0.1:8000/login",
    json={"employee_id": login_id, "password": login_password},
)
login_result = login_response.json()

if not login_result.get("success"):
    print("Login failed. Exiting.")
    exit()

current_employee_id = login_result["employee_id"]
print(f"\nWelcome, {login_result['name']}! ({login_result['role']})\n")

chat_history = []

print("EnterpriseAssist v4 (with login) — type 'exit' to quit\n")

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
            tools=tools,
        ),
    )

    print(f"AI: {response.text}\n")

    chat_history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))