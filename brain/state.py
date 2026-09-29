from dataclasses import dataclass, field
from typing import List

from brain.relationship import Relationship
from brain.needs import Needs


@dataclass
class BrainState:
    # -------------------------
    # Internal Simulation
    # -------------------------
    mood: str = "neutral"
    energy: int = 100
    focus: int = 100
    stress: int = 0
    current_goal: str = "Observe and assess."
    current_action: str = "Conversing with a visitor."
    
    relationship: Relationship = field(default_factory=Relationship)
    needs: Needs = field(default_factory=Needs)
    
    # -------------------------
    # Kurumi-Specific State
    # -------------------------
    time_bullets_remaining: int = 12  # Metaphorical - Zafkiel's 12 bullets
    shadow_activity: str = "dormant"  # dormant, stirring, active, manifested
    zafkiel_eye_state: str = "concealed"  # concealed, visible, glowing
    active_clones: int = 0  # From Het (8th Bullet)
    current_timeline_stability: float = 1.0  # 0-1, affects memory consistency
    
    # -------------------------
    # Reflection & Monologue
    # -------------------------
    last_monologue: str = ""
    last_reflection: str = ""
    
    # -------------------------
    # Human Interpretation
    # -------------------------
    descriptions: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)