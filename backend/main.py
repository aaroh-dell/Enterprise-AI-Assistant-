from fastapi import FastAPI
from backend.api import leave, tickets, employees, it, expenses, travel

app = FastAPI(title="Enterprise AI Assistant Backend")

app.include_router(leave.router)
app.include_router(tickets.router)
app.include_router(employees.router)
app.include_router(it.router)
app.include_router(expenses.router)
app.include_router(travel.router)

@app.get("/")
def root():
    return {"message": "Enterprise AI Assistant backend is running"}