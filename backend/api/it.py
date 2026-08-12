from fastapi import APIRouter

router = APIRouter()

@router.post("/it/password-reset")
def reset_password(employee_id: str):
    # Fake reset - in a real system this would trigger an actual reset flow
    return {"status": "password reset initiated", "employee_id": employee_id}