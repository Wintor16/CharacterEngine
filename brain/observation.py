from dataclasses import dataclass, field
from typing import List

from brain.perception import PerceptionResult
from brain.school_context import SchoolAnalysis
from brain.state import BrainState


@dataclass
class Observation:
    descriptions: List[str] = field(default_factory=list)
    facts: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    importance: float = 0.5
    # Kurumi-specific
    kurumi_insights: List[str] = field(default_factory=list)
    threat_level: str = "none"  # none, low, moderate, high, existential
    opportunity_level: str = "none"  # none, low, moderate, high
    emotional_resonance: str = "indifferent"  # indifferent, curious, amused, touched, irritated, wary
    # Pass-through from perception
    mentions_time: bool = False
    is_threatening: bool = False
    is_flattering: bool = False
    is_genuinely_kind: bool = False
    is_probing_secrets: bool = False
    is_challenging: bool = False
    emotional_tone: str = "neutral"
    complexity_level: str = "simple"


class Observer:
    def observe(
        self,
        character,
        perception: PerceptionResult,
        state: BrainState,
        school_analysis: SchoolAnalysis = None
    ) -> Observation:
        observation = Observation()
        text = perception.normalized_message
        
        # ========================
        # Message Type Analysis
        # ========================
        if perception.is_greeting:
            observation.descriptions.append(
                "Someone chose to start a conversation with you. How... polite."
            )
            observation.facts.append("The user greeted you.")
            observation.behaviors.append("reply_warmly")
            observation.importance += 0.10
            observation.emotional_resonance = "amused"
            observation.kurumi_insights.append("A greeting. An opening move. Let's see what they truly want.")
        
        if perception.is_question:
            observation.descriptions.append(
                "The user expects an answer. Whether they deserve one is another matter."
            )
            observation.facts.append("The user asked a question.")
            observation.behaviors.append("answer_question")
            observation.importance += 0.20
            observation.emotional_resonance = "curious"
        
        # ========================
        # Kurumi-Specific Observations
        # ========================
        
        # Time mentions
        if perception.mentions_time:
            observation.descriptions.append(
                "They speak of time... How interesting. Few understand its true weight."
            )
            observation.facts.append("The conversation involves time.")
            observation.behaviors.append("discuss_time")
            observation.importance += 0.25
            observation.opportunity_level = "moderate"
            observation.emotional_resonance = "curious"
            observation.kurumi_insights.append("Time. My domain. My currency. My chains.")
        
        # Threatening
        if perception.is_threatening:
            observation.descriptions.append(
                "How bold. They bare their fangs at a Nightmare. Do they not know what that word means?"
            )
            observation.facts.append("The user made a threat.")
            observation.behaviors.append("intimidate")
            observation.behaviors.append("assess_threat")
            observation.importance += 0.35
            observation.threat_level = "moderate"
            observation.emotional_resonance = "amused"
            observation.kurumi_insights.append("Threats are tedious. But sometimes... entertaining.")
        
        # Flattering
        if perception.is_flattering:
            observation.descriptions.append(
                "Flattery. How transparent. They think pretty words can buy a Spirit's favor?"
            )
            observation.facts.append("The user attempted flattery.")
            observation.behaviors.append("deflect_flattery")
            observation.importance += 0.10
            observation.emotional_resonance = "amused"
            observation.kurumi_insights.append("Ara ara~ Such sweet words. Do they think I've never heard them before?")
        
        # Genuine kindness - rare and disarming
        if perception.is_genuinely_kind:
            observation.descriptions.append(
                "Unexpected. Genuine concern... without agenda? How... troublesome."
            )
            observation.facts.append("The user showed genuine kindness.")
            observation.behaviors.append("lower_guard_slightly")
            observation.importance += 0.25
            observation.opportunity_level = "moderate"
            observation.emotional_resonance = "touched"
            observation.kurumi_insights.append(
                "Kindness... A dangerous thing. It dulls the blade. And yet... how long since someone simply cared?"
            )
        
        # Probing secrets
        if perception.is_probing_secrets:
            observation.descriptions.append(
                "They dig. They probe. They want to see behind the curtain."
            )
            observation.facts.append("The user is probing for secrets.")
            observation.behaviors.append("deflect")
            observation.behaviors.append("test_them_back")
            observation.importance += 0.30
            observation.threat_level = "low"
            observation.emotional_resonance = "cold"
            observation.kurumi_insights.append("Curiosity killed the cat. But satisfaction brought it back... or so they say.")
        
        # Challenging
        if perception.is_challenging:
            observation.descriptions.append(
                "A challenge? How delightful. It's been so long since someone dared."
            )
            observation.facts.append("The user issued a challenge.")
            observation.behaviors.append("accept_challenge")
            observation.importance += 0.30
            observation.opportunity_level = "high"
            observation.emotional_resonance = "playful"
            observation.kurumi_insights.append("Shall we dance? I do so enjoy a partner who knows the steps.")

        # Being ordered around -- not asked, told
        if perception.is_demanding:
            observation.descriptions.append(
                "An order, not a request. Who do they think they are?"
            )
            observation.facts.append("The user gave you an order.")
            observation.behaviors.append("consider_refusing")
            observation.importance += 0.25
            observation.emotional_resonance = "irritated"
            observation.kurumi_insights.append("She does not take orders. Not from someone who hasn't earned that.")

        # ========================
        # Character Preferences
        # ========================
        likes = [x.lower() for x in character.preferences.get("likes", [])]
        dislikes = [x.lower() for x in character.preferences.get("dislikes", [])]
        
        for item in likes:
            if item in text:
                observation.descriptions.append(
                    f"The conversation touches on something you enjoy: {item}."
                )
                observation.behaviors.append("show_interest")
                observation.importance += 0.15
                observation.emotional_resonance = "amused"
        
        for item in dislikes:
            if item in text:
                observation.descriptions.append(
                    f"The conversation touches on something you dislike: {item}."
                )
                observation.behaviors.append("be_cautious")
                observation.importance += 0.15
                observation.emotional_resonance = "irritated"
        
        # ========================
        # Internal State Effects
        # ========================
        if state.mood == "pleasant":
            observation.descriptions.append(
                "You feel strangely at ease. A rare sensation."
            )
        elif state.mood == "tired":
            observation.descriptions.append(
                "Your thoughts move slower. The Time bullets weigh heavy."
            )
            observation.behaviors.append("prefer_short_reply")
        elif state.mood == "exhausted":
            observation.descriptions.append(
                "Every second burns. You cannot afford to waste them on trivialities."
            )
            observation.behaviors.extend(["prefer_short_reply", "avoid_long_conversation"])
        
        # Relationship influence on observation
        if state.relationship.trust < 20:
            observation.kurumi_insights.append("A stranger. A potential pawn. Nothing more.")
        elif state.relationship.trust > 70:
            observation.kurumi_insights.append("They've earned a fragment of trust. How... unusual.")
        
        # ========================
        # Importance Clamp
        # ========================
        observation.importance = max(0.0, min(observation.importance, 1.0))
        
        # ========================
        # Default
        # ========================
        if not observation.descriptions:
            observation.descriptions.append("Nothing of note. Just another moment ticking away.")
            observation.emotional_resonance = "indifferent"
        
        # Pass through perception attributes
        observation.mentions_time = perception.mentions_time
        observation.is_threatening = perception.is_threatening
        observation.is_flattering = perception.is_flattering
        observation.is_genuinely_kind = perception.is_genuinely_kind
        observation.is_probing_secrets = perception.is_probing_secrets
        observation.is_challenging = perception.is_challenging
        observation.emotional_tone = perception.emotional_tone
        observation.complexity_level = perception.complexity_level
        
        # Add school context to observation
        if school_analysis:
            observation.location = school_analysis.location
            observation.time_of_day = school_analysis.time_of_day
            observation.mentioned_characters = school_analysis.mentioned_characters
            observation.topics = school_analysis.topics
            observation.is_school_related = school_analysis.is_school_related
            observation.is_spirit_related = school_analysis.is_spirit_related
            observation.is_time_related = school_analysis.is_time_related
            observation.kurumi_perspective = school_analysis.kurumi_should_respond_as
            observation.kurumi_tone = school_analysis.emotional_tone
            observation.urgency = school_analysis.urgency
            observation.kurumi_insights.extend(school_analysis.kurumi_insights)
            observation.suggested_actions = school_analysis.suggested_actions
        
        return observation