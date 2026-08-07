class ItAgent:
    def __init__(self):
        self.name = "IT"

    def handle(self, request: str):
        return {"agent": self.name, "response": f"IT handling: {request}"}
