from fastapi import APIRouter
from pydantic import BaseModel
import json

router = APIRouter()

with open("backend/data/employees.json") as f:
    employees = json.load(f)


@router.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    emp = employees.get(employee_id)
    if emp is None:
        return {"error": "Employee not found"}
    # Don't leak the password in lookups
    return {"employee_id": employee_id, "name": emp["name"], "department": emp["department"]}


class LoginRequest(BaseModel):
    employee_id: str
    password: str


@router.post("/login")
def login(request: LoginRequest):
    emp = employees.get(request.employee_id)
    if emp is None or emp["password"] != request.password:
        return {"success": False, "error": "Invalid employee ID or password"}
    return {
        "success": True,
        "employee_id": request.employee_id,
        "name": emp["name"],
        "role": emp["role"],
    }