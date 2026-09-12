from memory.storage import MemoryStorage
from memory.memory import Memory
from memory.retriever import MemoryRetriever
from memory.short_memory import ShortMemory


class MemoryManager:

    def __init__(
        self,
        short_memory_limit: int = 8
    ):

        self.storage = MemoryStorage()

        self.retriever = MemoryRetriever()

        self.short_memory = ShortMemory(
            limit=short_memory_limit
        )

        self.memories = self.storage.load()

    # ---------------------------------
    # Long Term Memory
    # ---------------------------------

    def add(
        self,
        memory: Memory
    ):

        self.memories.append(memory)

        self.storage.save(
            self.memories
        )

    def retrieve(
        self,
        query: str
    ):

        return self.retriever.retrieve(
            self.memories,
            query
        )

    def all(self):

        return self.memories

    # ---------------------------------
    # Short Term Conversation
    # ---------------------------------

    def add_message(
        self,
        role: str,
        content: str
    ):

        self.short_memory.add(
            role,
            content
        )

    def conversation(self):

        return self.short_memory.all()

    def clear_conversation(self):

        self.short_memory.clear()

    # ---------------------------------
    # Explicit Memory Save
    # ---------------------------------

    def save_memory(
        self,
        memory: Memory
    ):

        self.add(memory)