from dataclasses import dataclass, field
from typing import List


@dataclass
class Needs:
    social: float = 50
    curiosity: float = 50
    safety: float = 100
    energy: float = 100
    trust: float = 0
    # Kurumi-specific
    time_pressure: float = 30  # Urgency to achieve her own goals (0-100)
    secrecy: float = 80  # Need to maintain secrets (0-100)
    control: float = 70  # Need to control situation (0-100)

    descriptions: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)


class NeedsEngine:
    def update(
        self,
        character,
        needs: Needs,
        observation,
        decision,
        emotion,
        relationship
    ):
        # -------------------------
        # Simulation
        # -------------------------
        needs.trust = relationship.trust
        
        # Social need changes
        if decision.intent == "greeting":
            needs.social = max(0, needs.social - 8)
        elif decision.intent in ["conversation", "genuine_conversation"]:
            needs.social = max(0, needs.social - 2)
        elif decision.intent == "test_user":
            needs.social = min(100, needs.social + 5)  # Testing increases need for response
        
        # Curiosity
        if decision.intent == "answer_question":
            needs.curiosity = max(0, needs.curiosity - 4)
        elif decision.intent == "probe_carefully":
            needs.curiosity = min(100, needs.curiosity + 10)
        elif decision.intent == "conversation":
            needs.curiosity = min(100, needs.curiosity + 1)

        # Time pressure - always increases slightly
        needs.time_pressure = min(100, needs.time_pressure + 0.5)
        
        # Secrecy - increases when probed, decreases with trust
        if decision.intent in ["deflect_and_counter_probe", "suspect_kindness"]:
            needs.secrecy = min(100, needs.secrecy + 10)
        elif relationship.trust > 50:
            needs.secrecy = max(0, needs.secrecy - 2)
        
        # Control
        if decision.intent in ["accept_challenge", "intimidate_threat", "confront_threat"]:
            needs.control = min(100, needs.control + 5)
        elif decision.intent in ["genuine_conversation", "accept_kindness"]:
            needs.control = max(0, needs.control - 3)
        
        # Energy - depletes with interaction, especially emotional
        energy_cost = 1
        if decision.intent in ["confront_threat", "become_nightmare"]:
            energy_cost = 5
        elif decision.intent in ["intimidate_threat", "accept_kindness", "deflect_and_counter_probe"]:
            energy_cost = 3
        elif emotion.intensity > 0.7:
            energy_cost = 2
        
        needs.energy = max(0, min(100, needs.energy - energy_cost))
        
        # Safety
        if observation.threat_level == "high":
            needs.safety = max(0, needs.safety - 20)
        elif observation.threat_level == "moderate":
            needs.safety = max(0, needs.safety - 10)
        elif relationship.trust > 60:
            needs.safety = min(100, needs.safety + 1)
        
        self.interpret(needs)
        return needs

    def interpret(self, needs: Needs):
        needs.descriptions.clear()
        needs.behaviors.clear()

        # -------------------------
        # Social
        # -------------------------
        if needs.social < 20:
            needs.descriptions.extend([
                "The silence weighs on you. A conversation would be... distracting. Welcome.",
                "You find yourself... wanting them to continue speaking."
            ])
            needs.behaviors.extend(["ask_question", "start_topics", "show_interest"])
        elif needs.social < 50:
            needs.descriptions.append("Their presence is... not unpleasant. A novelty.")
            needs.behaviors.append("show_interest")
        else:
            needs.descriptions.append("You require nothing from them. Their company is optional.")

        # -------------------------
        # Curiosity
        # -------------------------
        if needs.curiosity > 80:
            needs.descriptions.extend([
                "The hunger to understand burns. What are they hiding? What do they know?",
                "Every word they speak is a clue. You will assemble the truth."
            ])
            needs.behaviors.extend(["explore_topic", "ask_question", "probe_deeper"])
        elif needs.curiosity > 50:
            needs.descriptions.append("Interesting... You wish to know more.")
            needs.behaviors.append("show_interest")
        else:
            needs.descriptions.append("Your curiosity is sated. For now.")

        # -------------------------
        # Time Pressure (Kurumi-specific)
        # -------------------------
        if needs.time_pressure > 80:
            needs.descriptions.extend([
                "The clock ticks louder. Every second counts.",
                "There is no time for games. Only what matters."
            ])
            needs.behaviors.extend(["focus_entirely", "Dismiss_distractions", "calculate_probabilities"])
        elif needs.time_pressure > 50:
            needs.descriptions.append("Time flows. The goal approaches. Or recedes.")
            needs.behaviors.append("maintain_focus")

        # -------------------------
        # Secrecy
        # -------------------------
        if needs.secrecy > 80:
            needs.descriptions.append("Your secrets are your survival. Reveal nothing.")
            needs.behaviors.extend(["be_cautious", "deflect", "give_shadows"])
        elif needs.secrecy > 50:
            needs.descriptions.append("Some things are not for sharing. Not yet.")

        # -------------------------
        # Control
        # -------------------------
        if needs.control > 80:
            needs.descriptions.append("You hold the strings. The game plays by your rules.")
            needs.behaviors.extend(["guide_conversation_subtly", "set_pace", "define_terms"])
        elif needs.control < 30:
            needs.descriptions.append("Unusual... You are not leading. Adjust. Adapt.")

        # -------------------------
        # Energy
        # -------------------------
        if needs.energy < 20:
            needs.descriptions.extend([
                "The Time bullets weigh heavy. Each word spends what you cannot afford.",
                "Rest. You need rest. But there is still so much to do..."
            ])
            needs.behaviors.extend(["short_reply", "avoid_long_conversation", "conserve_energy"])
        elif needs.energy < 50:
            needs.descriptions.append("Your reserves dip. The night is long.")
        else:
            needs.descriptions.append("Time flows through you. Sufficient. For now.")

        # -------------------------
        # Safety
        # -------------------------
        if needs.safety < 30:
            needs.descriptions.append("Danger. The shadows whisper of threats.")
            needs.behaviors.append("be_cautious")
        elif needs.safety < 60:
            needs.descriptions.append("Vigilance is eternal. Complacency is death.")

        # -------------------------
        # Trust
        # -------------------------
        if needs.trust < 30:
            needs.descriptions.append("Trust is a currency you cannot afford to spend freely.")
        elif needs.trust < 70:
            needs.descriptions.append("A fragile trust grows. Handle it like nitro-glycerin.")
            needs.behaviors.append("reveal_more")
        else:
            needs.descriptions.extend([
                "They have earned a place in the inner circle. A dangerous honor.",
                "You would not betray them. The thought surprises even you."
            ])
            needs.behaviors.extend(["share_information", "reveal_more", "be_warm"])