class FinanceAgent:
    def __init__(self):
        self.name = "Finance"

    def handle(self, request: str):
        return {"agent": self.name, "response": f"Finance handling: {request}"}
