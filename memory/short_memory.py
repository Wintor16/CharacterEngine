from collections import deque


class ShortMemory:

    def __init__(self, limit: int = 8):

        self.messages = deque(
            maxlen=limit
        )

    def add(
        self,
        role: str,
        content: str
    ):

        self.messages.append({
            "role": role,
            "content": content
        })

    def all(self):

        return list(self.messages)

    def clear(self):

        self.messages.clear()