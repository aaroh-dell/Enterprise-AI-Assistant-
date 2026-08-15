from fastapi import APIRouter
from backend.database import SessionLocal, Ticket

router = APIRouter()


@router.post("/tickets")
def create_ticket(employee_id: str, issue: str):
    db = SessionLocal()
    ticket = Ticket(employee_id=employee_id, issue=issue, status="open")
    db.add(ticket)
    db.commit()
    db.refresh(ticket)  # pulls the auto-generated ticket_id back into the object
    db.close()

    return {
        "ticket_id": ticket.ticket_id,
        "employee_id": ticket.employee_id,
        "issue": ticket.issue,
        "status": ticket.status,
    }


@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    db = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    db.close()

    if ticket is None:
        return {"error": "Ticket not found"}
    return {
        "ticket_id": ticket.ticket_id,
        "employee_id": ticket.employee_id,
        "issue": ticket.issue,
        "status": ticket.status,
    }