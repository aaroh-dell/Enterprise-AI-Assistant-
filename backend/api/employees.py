from fastapi import APIRouter

router = APIRouter()

employees = {
    "101": {"name": "Aaroh", "department": "Engineering"},
    "102": {"name": "Priya", "department": "HR"},
}

@router.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    emp = employees.get(employee_id)
    if emp is None:
        return {"error": "Employee not found"}
    return {"employee_id": employee_id, **emp}