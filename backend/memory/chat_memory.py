class ChatMemory:
    def __init__(self):
        self.messages = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_history(self):
        return self.messages
