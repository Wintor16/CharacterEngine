from dataclasses import dataclass, field

from brain.decision import Decision
from brain.emotion import Emotion
from brain.needs import Needs
from brain.observation import Observation
from brain.planner import DialoguePlan
from brain.reasoning import Reasoning
from brain.relationship import Relationship
from brain.state import BrainState
from brain.thought import Thought
from memory.memory import Memory


@dataclass
class BrainContext:

    # Brain State
    state: BrainState

    # Perception Result
    observation: Observation

    # Decision
    decision: Decision

    # Internal Systems
    emotion: Emotion

    relationship: Relationship

    needs: Needs

    # Internal Thoughts
    thoughts: list[Thought] = field(default_factory=list)

    reasoning: Reasoning | None = None

    # Final Response Plan
    plan: DialoguePlan | None = None

    # Memories
    memories: list[Memory] = field(default_factory=list)