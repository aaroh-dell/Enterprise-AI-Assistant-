import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Explicitly locate .env relative to this file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ---------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True)
    name = Column(String)
    department = Column(String)
    password = Column(String)
    role = Column(String)
    leave_balance = Column(Integer)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    reason = Column(String)


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String)
    issue = Column(String)
    status = Column(String)


class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String)
    amount = Column(Float)
    category = Column(String)
    description = Column(String)
    status = Column(String)


class TravelRequestDB(Base):
    __tablename__ = "travel_requests"

    travel_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String)
    destination = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    purpose = Column(String)
    status = Column(String)


Base.metadata.create_all(bind=engine)