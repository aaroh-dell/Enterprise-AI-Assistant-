from fastapi import APIRouter

router = APIRouter(prefix="/leave", tags=["leave"])

@router.get("/")
def get_leave_status():
    return {"status": "Leave API ready"}
