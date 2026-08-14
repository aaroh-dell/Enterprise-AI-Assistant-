from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TravelRequest(BaseModel):
    employee_id: str
    destination: str
    start_date: str
    end_date: str
    purpose: str

travel_requests = []
next_travel_id = 1

# Simple flat per-day rate for budget estimation - domestic vs international
DOMESTIC_KEYWORDS = {"mumbai", "delhi", "bangalore", "pune", "chennai", "hyderabad", "kolkata"}

@router.post("/travel")
def request_travel(request: TravelRequest):
    global next_travel_id
    travel = {
        "travel_id": next_travel_id,
        "employee_id": request.employee_id,
        "destination": request.destination,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "purpose": request.purpose,
        "status": "pending",
    }
    travel_requests.append(travel)
    next_travel_id += 1
    return travel


@router.get("/travel/{travel_id}")
def get_travel_status(travel_id: int):
    for t in travel_requests:
        if t["travel_id"] == travel_id:
            return t
    return {"error": "Travel request not found"}


@router.get("/travel/budget/estimate")
def estimate_budget(destination: str, days: int):
    is_domestic = destination.strip().lower() in DOMESTIC_KEYWORDS
    daily_rate = 4000 if is_domestic else 15000  # INR, flat fake rate
    total = daily_rate * days
    return {
        "destination": destination,
        "days": days,
        "trip_type": "domestic" if is_domestic else "international",
        "daily_rate": daily_rate,
        "estimated_total": total,
    }