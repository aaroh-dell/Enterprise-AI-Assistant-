from fastapi import APIRouter

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/")
def get_employees():
    return {"status": "Employees API ready"}
