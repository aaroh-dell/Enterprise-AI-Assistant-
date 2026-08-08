from fastapi import APIRouter

router = APIRouter()

tickets = []  # fake in-memory database
next_id = 1

@router.post("/tickets")
def create_ticket(employee_id: str, issue: str):
    global next_id
    ticket = {"ticket_id": next_id, "employee_id": employee_id, "issue": issue, "status": "open"}
    tickets.append(ticket)
    next_id += 1
    return ticket

@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    for t in tickets:
        if t["ticket_id"] == ticket_id:
            return t
    return {"error": "Ticket not found"}