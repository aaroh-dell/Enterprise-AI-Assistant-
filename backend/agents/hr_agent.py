class HrAgent:
    def __init__(self):
        self.name = "HR"

    def handle(self, request: str):
        return {"agent": self.name, "response": f"HR handling: {request}"}
