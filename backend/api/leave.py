from fastapi import APIRouter

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