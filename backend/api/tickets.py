from fastapi import APIRouter

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("/")
def get_tickets():
    return {"status": "Tickets API ready"}
