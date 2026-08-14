from fastapi import APIRouter
from pydantic import BaseModel
import json

router = APIRouter()

with open("backend/data/employees.json") as f:
    employees_data = json.load(f)


@router.get("/leave/{employee_id}")
def get_leave_balance(employee_id: str):
    emp = employees_data.get(employee_id)
    if emp is None:
        return {"error": "Employee not found"}
    return {"employee_id": employee_id, "leave_balance": emp["leave_balance"]}


class LeaveRequest(BaseModel):
    employee_id: str
    start_date: str
    end_date: str
    reason: str

leave_requests = []

@router.post("/leave/apply")
def apply_leave(request: LeaveRequest):
    if request.employee_id not in employees_data:
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