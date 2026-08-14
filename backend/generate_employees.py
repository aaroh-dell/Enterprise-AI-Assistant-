import random
from faker import Faker
from backend.database import SessionLocal, Employee

fake = Faker()
departments = ["Engineering", "HR", "Finance", "IT", "Travel", "Sales", "Marketing"]

db = SessionLocal()

# Clear existing data first, so re-running this script doesn't create duplicates
db.query(Employee).delete()

for i in range(101, 1101):
    emp = Employee(
        employee_id=str(i),
        name=fake.name(),
        department=random.choice(departments),
        password=fake.password(length=8),
        role="hr" if random.random() < 0.05 else "employee",
        leave_balance=random.randint(0, 25),
    )
    db.add(emp)

db.commit()
db.close()

print("Generated 1000 employees in PostgreSQL.")