from dataclasses import dataclass


@dataclass
class AIResponse:

    text: str

    model: str

    generation_time: float

    success: bool = True

    error: str = ""