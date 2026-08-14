from fastapi import APIRouter
from pydantic import BaseModel
from backend.database import SessionLocal, Employee

router = APIRouter()


@router.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    db.close()

    if emp is None:
        return {"error": "Employee not found"}
    return {"employee_id": emp.employee_id, "name": emp.name, "department": emp.department}


class LoginRequest(BaseModel):
    employee_id: str
    password: str


@router.post("/login")
def login(request: LoginRequest):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()
    db.close()

    if emp is None or emp.password != request.password:
        return {"success": False, "error": "Invalid employee ID or password"}
    return {
        "success": True,
        "employee_id": emp.employee_id,
        "name": emp.name,
        "role": emp.role,
    }