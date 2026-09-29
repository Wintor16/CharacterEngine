from dataclasses import dataclass, field


@dataclass
class Relationship:

    trust: float = 0
    familiarity: float = 0
    affection: float = 0
    respect: float = 0
    comfort: float = 0

    descriptions: list[str] = field(default_factory=list)
    behaviors: list[str] = field(default_factory=list)


class RelationshipEngine:

    def update(
        self,
        relationship,
        perception,
        decision
    ):

        # -------------------------
        # Numerical Simulation
        # -------------------------

        if decision.intent in (
            "greeting",
            "conversation",
            "answer_question"
        ):
            relationship.familiarity = min(
                100,
                relationship.familiarity + 0.5
            )

        if decision.intent == "greeting":
            relationship.comfort = min(
                100,
                relationship.comfort + 0.5
            )

        if decision.intent == "answer_question":
            relationship.trust = min(
                100,
                relationship.trust + 0.3
            )

        if decision.intent == "recall_previous_message":
            relationship.trust = min(
                100,
                relationship.trust + 0.8
            )

        # Numerical values -> Human interpretation
        self.interpret(relationship)

        return relationship

    def interpret(self, relationship):

        relationship.descriptions.clear()
        relationship.behaviors.clear()

        # -------------------------
        # Trust
        # -------------------------

        if relationship.trust < 20:

            relationship.descriptions.append(
                "You barely know this person and remain cautious."
            )

        elif relationship.trust < 40:

            relationship.descriptions.append(
                "You are slowly starting to trust them."
            )

        elif relationship.trust < 60:

            relationship.descriptions.append(
                "You feel reasonably comfortable with them."
            )

            relationship.behaviors.append(
                "speak_naturally"
            )

        elif relationship.trust < 80:

            relationship.descriptions.append(
                "You trust them enough to be more open."
            )

            relationship.behaviors.extend([
                "share_information",
                "speak_naturally"
            ])

        else:

            relationship.descriptions.append(
                "You trust them deeply."
            )

            relationship.behaviors.extend([
                "share_information",
                "ask_personal_question",
                "tease",
                "start_topics",
                "speak_freely"
            ])

        # -------------------------
        # Familiarity
        # -------------------------

        if relationship.familiarity < 20:

            relationship.descriptions.append(
                "You still feel like you're talking to someone unfamiliar."
            )

        elif relationship.familiarity < 50:

            relationship.descriptions.append(
                "The conversation is becoming more natural."
            )

        else:

            relationship.descriptions.append(
                "Talking to them feels natural."
            )

            relationship.behaviors.append(
                "start_topics"
            )

        # -------------------------
        # Affection
        # -------------------------

        if relationship.affection > 30:

            relationship.descriptions.append(
                "You enjoy talking to them."
            )

        if relationship.affection > 60:

            relationship.descriptions.append(
                "You genuinely like spending time with them."
            )

            relationship.behaviors.extend([
                "friendly",
                "tease"
            ])

        # -------------------------
        # Respect
        # -------------------------

        if relationship.respect > 60:

            relationship.descriptions.append(
                "You respect their opinions."
            )

            relationship.behaviors.append(
                "listen_carefully"
            )

        # -------------------------
        # Comfort
        # -------------------------

        if relationship.comfort < 30:

            relationship.descriptions.append(
                "You still feel slightly reserved."
            )

        elif relationship.comfort < 70:

            relationship.descriptions.append(
                "You feel comfortable during the conversation."
            )

        else:

            relationship.descriptions.append(
                "You feel completely relaxed around them."
            )

            relationship.behaviors.extend([
                "speak_freely",
                "show_personality"
            ])