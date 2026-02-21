class SessionMemory:

    def __init__(self, max_len=10):
        self.history = []
        self.max_len = max_len

    def add(self, role, content):

        self.history.append({
            "role": role,
            "content": content
        })
        if len(self.history) > self.max_len:
            self.history.pop(0)

    def get(self):
        return self.history

    def clear(self):
        self.history = []
