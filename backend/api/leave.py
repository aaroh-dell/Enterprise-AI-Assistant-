from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


# Fake in-memory "database" - just a Python dict for now
leave_balances = {
    "101": 12,
    "102": 5,
    "103": 20,
}

@router.get("/leave/{employee_id}")
def get_leave_balance(employee_id: str):
    balance = leave_balances.get(employee_id)
    if balance is None:
        return {"error": "Employee not found"}
    return {"employee_id": employee_id, "leave_balance": balance}

class LeaveRequest(BaseModel):
    employee_id: str
    start_date: str
    end_date: str
    reason: str

# Fake in-memory storage for submitted leave requests
leave_requests = []

@router.post("/leave/apply")
def apply_leave(request: LeaveRequest):
    # Deduct the requested leave from balance (simple version - no day-counting logic yet)
    if request.employee_id not in leave_balances:
        return {"error": "Employee not found"}

    leave_requests.append(request.dict())
    return {
        "status": "submitted",
        "employee_id": request.employee_id,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "reason": request.reason,
    }

holidays = [
    {"date": "2026-10-02", "name": "Gandhi Jayanti"},
    {"date": "2026-12-25", "name": "Christmas"},
    {"date": "2027-01-01", "name": "New Year's Day"},
]

@router.get("/holidays")
def get_holidays():
    return holidays