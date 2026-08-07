class TravelAgent:
    def __init__(self):
        self.name = "Travel"

    def handle(self, request: str):
        return {"agent": self.name, "response": f"Travel handling: {request}"}
