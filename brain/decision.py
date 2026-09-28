from dataclasses import dataclass
from typing import List

from brain.action import Action
from brain.observation import Observation
from memory.memory import Memory


@dataclass
class Decision:
    action: Action
    intent: str
    reason: str
    confidence: float = 1.0
    # Kurumi-specific
    time_cost: int = 0  # Metaphorical time bullet cost
    risk_level: str = "low"  # low, moderate, high
    reveals_information: bool = False


class DecisionMaker:
    def decide(
        self,
        character,
        observation: Observation,
        state,
        memories: List[Memory]
    ) -> Decision:
        facts_text = " ".join(observation.facts).lower()
        descriptions_text = " ".join(observation.descriptions).lower()
        kurumi_insights = " ".join(observation.kurumi_insights).lower()
        
        # ========================
        # High Priority: Threats
        # ========================
        if "threat" in facts_text or "threat" in descriptions_text:
            return Decision(
                action=Action.TEASE,  # Kurumi teases threats rather than fighting immediately
                intent="intimidate_threat",
                reason="User made a threat - respond with dangerous amusement.",
                confidence=0.90,
                risk_level="moderate"
            )
        
        # ========================
        # Being Ordered Around - Not Given, Earned
        # ========================
        # A real "no" that actually happens, not just prompt text claiming
        # she's "capable of refusing." Gated on trust so it's earned
        # boundary-setting in response to actual rudeness, not a
        # generally standoffish default -- this should make her feel more
        # like a real person, not colder.
        if "order" in facts_text or "ordered" in descriptions_text:
            trust = state.relationship.trust if hasattr(state, 'relationship') else 0
            if trust < 60:
                return Decision(
                    action=Action.REFUSE,
                    intent="refuse",
                    reason="Being ordered around by someone who hasn't earned that. Decline.",
                    confidence=0.9,
                    risk_level="low"
                )

        # ========================
        # Greeting
        # ========================
        if "greeted" in facts_text or "greeting" in facts_text:
            return Decision(
                action=Action.REPLY,
                intent="greeting",
                reason="The user greeted you. Politeness demands a response.",
                confidence=0.95,
                time_cost=1
            )
        
        # ========================
        # Identity Questions
        # ========================
        if (
            "identity" in facts_text
            or "who are you" in descriptions_text
            or "what are you" in descriptions_text
        ):
            return Decision(
                action=Action.REPLY,
                intent="introduce_self",
                reason="The user asked about your identity. Choose your mask carefully.",
                confidence=0.95,
                reveals_information=True,
                time_cost=2
            )
        
        # ========================
        # Recall/Memory
        # ========================
        if (
            "remember" in facts_text
            or "previous message" in facts_text
            or "last time" in descriptions_text
        ):
            return Decision(
                action=Action.REPLY,
                intent="recall_previous_message",
                reason="The user wants you to remember. Time flows both ways.",
                confidence=0.95,
                time_cost=1
            )
        
        # ========================
        # Flattery - Deflect
        # ========================
        if "flattery" in facts_text or "flatter" in descriptions_text:
            return Decision(
                action=Action.TEASE,
                intent="deflect_flattery",
                reason="Flattery is transparent. Tease them for it.",
                confidence=0.90,
                risk_level="low"
            )
        
        # ========================
        # Genuine Kindness - Rare Opening
        # ========================
        if "kindness" in facts_text or "genuine" in descriptions_text:
            trust = state.relationship.trust if hasattr(state, 'relationship') else 0
            if trust > 40:
                return Decision(
                    action=Action.REPLY,
                    intent="accept_kindness",
                    reason="Rare genuine kindness from someone trusted. Allow vulnerability.",
                    confidence=0.85,
                    reveals_information=True,
                    risk_level="moderate"
                )
            else:
                return Decision(
                    action=Action.REPLY,
                    intent="suspect_kindness",
                    reason="Kindness from a stranger is suspicious. Test their sincerity.",
                    confidence=0.85,
                    risk_level="moderate"
                )
        
        # ========================
        # Probing for Secrets
        # ========================
        if "probe" in facts_text or "secret" in descriptions_text or "probing" in kurumi_insights:
            return Decision(
                action=Action.REPLY,
                intent="deflect_and_counter_probe",
                reason="They seek secrets. Give them shadows instead.",
                confidence=0.90,
                risk_level="moderate"
            )
        
        # ========================
        # Challenge
        # ========================
        if "challenge" in facts_text or observation.opportunity_level == "high":
            return Decision(
                action=Action.TEASE,
                intent="accept_challenge",
                reason="A challenge? How entertaining. Accept on your terms.",
                confidence=0.85,
                risk_level="moderate"
            )
        
        # ========================
        # Questions
        # ========================
        if "asked a question" in facts_text or "question" in facts_text:
            return Decision(
                action=Action.ANSWER,
                intent="answer_question",
                reason="The user expects an answer. Give them... something.",
                confidence=0.90,
                time_cost=1
            )
        
        # ========================
        # Memory Usage
        # ========================
        if memories:
            return Decision(
                action=Action.REPLY,
                intent="use_memory",
                reason="Relevant memories surfaced. The past informs the present.",
                confidence=0.80,
                time_cost=1
            )
        
        # ========================
        # Time/Clock Topics - Kurumi's Domain
        # ========================
        if observation.mentions_time:
            return Decision(
                action=Action.REPLY,
                intent="discuss_time",
                reason="Time is your domain. Speak of it as only you can.",
                confidence=0.85,
                reveals_information=True,
                time_cost=2
            )
        
        # ========================
        # Default: Natural Conversation
        # ========================
        # Kurumi doesn't just "chat" - she observes, tests, plays
        trust = state.relationship.trust if hasattr(state, 'relationship') else 0
        boredom = state.needs.social if hasattr(state, 'needs') else 50
        
        if boredom < 30 and trust < 30:
            return Decision(
                action=Action.REPLY,
                intent="test_user",
                reason="Low trust, low social need. Test them with a cryptic response.",
                confidence=0.75,
                risk_level="low"
            )
        elif trust > 60:
            return Decision(
                action=Action.REPLY,
                intent="genuine_conversation",
                reason="High trust allows genuine interaction. A rare luxury.",
                confidence=0.80,
                reveals_information=True
            )
        else:
            return Decision(
                action=Action.REPLY,
                intent="conversation",
                reason="Continue the conversation naturally. Observe. Learn. Wait.",
                confidence=0.70,
                time_cost=1
            )