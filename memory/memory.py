from dataclasses import dataclass, field


@dataclass
class Memory:

    # -----------------------------
    # Core
    # -----------------------------

    title: str

    content: str

    # -----------------------------
    # Importance
    # -----------------------------

    importance: float = 0.5

    # -----------------------------
    # Categorization
    # -----------------------------

    category: str = "general"

    tags: list[str] = field(default_factory=list)

    # -----------------------------
    # Emotional Context
    # -----------------------------

    emotion: str = ""

    # -----------------------------
    # Related People
    # -----------------------------

    people: list[str] = field(default_factory=list)

    # -----------------------------
    # Usage
    # -----------------------------

    created_at: str = ""

    last_access: str = ""

    access_count: int = 0

    # -----------------------------
    # Future Semantic Search
    # -----------------------------

    embedding: list[float] = field(default_factory=list)