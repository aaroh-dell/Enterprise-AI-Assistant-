import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
BASE_URL = "http://127.0.0.1:8000"


def build_tools(employee_id: str):
    """Creates tool functions bound to the logged-in employee's ID -
    the AI can no longer act as a different employee than who's logged in."""

    def get_my_leave_balance():
        """Fetch the logged-in employee's leave balance."""
        return requests.get(f"{BASE_URL}/leave/{employee_id}").json()

    def get_my_info():
        """Fetch the logged-in employee's name and department."""
        return requests.get(f"{BASE_URL}/employees/{employee_id}").json()

    def create_ticket(issue: str):
        """Create an IT support ticket for the logged-in employee."""
        return requests.post(f"{BASE_URL}/tickets", params={"employee_id": employee_id, "issue": issue}).json()

    def submit_leave(start_date: str, end_date: str, reason: str):
        """Submit a leave application for the logged-in employee."""
        return requests.post(f"{BASE_URL}/leave/apply", json={
            "employee_id": employee_id, "start_date": start_date, "end_date": end_date, "reason": reason
        }).json()

    def get_holiday_calendar():
        """Fetch the company holiday calendar."""
        return requests.get(f"{BASE_URL}/holidays").json()

    def reset_my_password():
        """Trigger a password reset for the logged-in employee's account."""
        return requests.post(f"{BASE_URL}/it/password-reset", params={"employee_id": employee_id}).json()

    def check_ticket_status(ticket_id: int):
        """Check the status of an IT support ticket by its ID."""
        return requests.get(f"{BASE_URL}/tickets/{ticket_id}").json()

    def submit_expense(amount: float, category: str, description: str):
        """Submit an expense reimbursement claim for the logged-in employee."""
        return requests.post(f"{BASE_URL}/expenses", json={
            "employee_id": employee_id, "amount": amount, "category": category, "description": description
        }).json()

    def check_reimbursement_status(expense_id: int):
        """Check the status of an expense reimbursement claim by its ID."""
        return requests.get(f"{BASE_URL}/expenses/{expense_id}").json()

    def request_travel(destination: str, start_date: str, end_date: str, purpose: str):
        """Submit a business travel request for the logged-in employee."""
        return requests.post(f"{BASE_URL}/travel", json={
            "employee_id": employee_id, "destination": destination,
            "start_date": start_date, "end_date": end_date, "purpose": purpose
        }).json()

    def check_travel_status(travel_id: int):
        """Check the status of a submitted travel request by its ID."""
        return requests.get(f"{BASE_URL}/travel/{travel_id}").json()

    def estimate_travel_budget(destination: str, days: int):
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
- Assume the current year is 2026 unless the user explicitly specifies it.
"""


def get_ai_response(chat_history, user_input, employee_id):
    tools = build_tools(employee_id)
    chat_history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=chat_history,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, tools=tools),
    )

    chat_history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
    return response.text