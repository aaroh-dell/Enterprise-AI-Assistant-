from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ExpenseRequest(BaseModel):
    employee_id: str
    amount: float
    category: str
    description: str

expenses = []
next_expense_id = 1

@router.post("/expenses")
def submit_expense(request: ExpenseRequest):
    global next_expense_id
    expense = {
        "expense_id": next_expense_id,
        "employee_id": request.employee_id,
        "amount": request.amount,
        "category": request.category,
        "description": request.description,
        "status": "pending",
    }
    expenses.append(expense)
    next_expense_id += 1
    return expense

@router.get("/expenses/{expense_id}")
def get_expense_status(expense_id: int):
    for e in expenses:
        if e["expense_id"] == expense_id:
            return e
    return {"error": "Expense not found"}