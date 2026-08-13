import json
import random
from faker import Faker

fake = Faker()
departments = ["Engineering", "HR", "Finance", "IT", "Travel", "Sales", "Marketing"]

employees = {}
for i in range(101, 1101):  # 1000 employees, IDs 101-1100
    emp_id = str(i)
    employees[emp_id] = {
        "name": fake.name(),
        "department": random.choice(departments),
        "password": fake.password(length=8),
        "role": "hr" if random.random() < 0.05 else "employee",  # ~5% are HR
    }

with open("backend/data/employees.json", "w") as f:
    json.dump(employees, f, indent=2)

print(f"Generated {len(employees)} employees.")