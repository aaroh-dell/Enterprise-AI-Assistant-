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


Base.metadata.create_all(bind=engine)