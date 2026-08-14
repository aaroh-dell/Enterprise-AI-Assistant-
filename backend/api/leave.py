from fastapi import APIRouter
from pydantic import BaseModel
from backend.database import SessionLocal, Employee

router = APIRouter()


@router.get("/leave/{employee_id}")
def get_leave_balance(employee_id: str):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    db.close()

    if emp is None:
        return {"error": "Employee not found"}
    return {"employee_id": emp.employee_id, "leave_balance": emp.leave_balance}


class LeaveRequest(BaseModel):
    employee_id: str
    start_date: str
    end_date: str
    reason: str

leave_requests = []  # still in-memory for now - Step 9 will migrate this too

@router.post("/leave/apply")
def apply_leave(request: LeaveRequest):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()
    db.close()

    if emp is None:
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