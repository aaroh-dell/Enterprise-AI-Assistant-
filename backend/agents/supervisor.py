class SupervisorAgent:
    def __init__(self):
        self.name = "Supervisor"

    def route(self, user_query: str):
        return {"agent": "general", "query": user_query}
