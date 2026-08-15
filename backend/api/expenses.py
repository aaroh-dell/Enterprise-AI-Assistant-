from fastapi import APIRouter
from pydantic import BaseModel
from backend.database import SessionLocal, Expense

router = APIRouter()

class ExpenseRequest(BaseModel):
    employee_id: str
    amount: float
    category: str
    description: str


@router.post("/expenses")
def submit_expense(request: ExpenseRequest):
    db = SessionLocal()
    expense = Expense(
        employee_id=request.employee_id,
        amount=request.amount,
        category=request.category,
        description=request.description,
        status="pending",
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    db.close()

    return {
        "expense_id": expense.expense_id,
        "employee_id": expense.employee_id,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description,
        "status": expense.status,
    }


@router.get("/expenses/{expense_id}")
def get_expense_status(expense_id: int):
    db = SessionLocal()
    expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    db.close()

    if expense is None:
        return {"error": "Expense not found"}
    return {
        "expense_id": expense.expense_id,
        "employee_id": expense.employee_id,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description,
        "status": expense.status,
    }