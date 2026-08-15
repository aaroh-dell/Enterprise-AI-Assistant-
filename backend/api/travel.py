from fastapi import APIRouter
from pydantic import BaseModel
from backend.database import SessionLocal, TravelRequestDB

router = APIRouter()

class TravelRequest(BaseModel):
    employee_id: str
    destination: str
    start_date: str
    end_date: str
    purpose: str

DOMESTIC_KEYWORDS = {"mumbai", "delhi", "bangalore", "pune", "chennai", "hyderabad", "kolkata"}


@router.post("/travel")
def request_travel(request: TravelRequest):
    db = SessionLocal()
    travel = TravelRequestDB(
        employee_id=request.employee_id,
        destination=request.destination,
        start_date=request.start_date,
        end_date=request.end_date,
        purpose=request.purpose,
        status="pending",
    )
    db.add(travel)
    db.commit()
    db.refresh(travel)
    db.close()

    return {
        "travel_id": travel.travel_id,
        "employee_id": travel.employee_id,
        "destination": travel.destination,
        "start_date": travel.start_date,
        "end_date": travel.end_date,
        "purpose": travel.purpose,
        "status": travel.status,
    }


@router.get("/travel/{travel_id}")
def get_travel_status(travel_id: int):
    db = SessionLocal()
    travel = db.query(TravelRequestDB).filter(TravelRequestDB.travel_id == travel_id).first()
    db.close()

    if travel is None:
        return {"error": "Travel request not found"}
    return {
        "travel_id": travel.travel_id,
        "employee_id": travel.employee_id,
        "destination": travel.destination,
        "start_date": travel.start_date,
        "end_date": travel.end_date,
        "purpose": travel.purpose,
        "status": travel.status,
    }


@router.get("/travel/budget/estimate")
def estimate_budget(destination: str, days: int):
    is_domestic = destination.strip().lower() in DOMESTIC_KEYWORDS
    daily_rate = 4000 if is_domestic else 15000
    total = daily_rate * days
    return {
        "destination": destination,
        "days": days,
        "trip_type": "domestic" if is_domestic else "international",
        "daily_rate": daily_rate,
        "estimated_total": total,
    }