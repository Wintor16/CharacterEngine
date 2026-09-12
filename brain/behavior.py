from dataclasses import dataclass, field


@dataclass
class BehaviorResult:

    instructions: list[str] = field(default_factory=list)

    tone: str | None = None

    response_length: str | None = None

    reveal_information: str | None = None

    initiative: str | None = None


class BehaviorInterpreter:

    def interpret(
        self,
        behaviors: list[str]
    ) -> BehaviorResult:

        result = BehaviorResult()

        behavior_map = {

            # -------------------------
            # Emotion
            # -------------------------

            "be_warm": {
                "instruction":
                    "Speak warmly."
            },

            "be_positive": {
                "instruction":
                    "Keep an optimistic attitude."
            },

            "express_emotion": {
                "instruction":
                    "Let your emotions naturally influence your wording."
            },

            "be_cautious": {
                "instruction":
                    "Avoid revealing everything immediately."
            },

            # -------------------------
            # Conversation
            # -------------------------

            "pause": {
                "instruction":
                    "Think briefly before answering."
            },

            "short_reply": {
                "instruction":
                    "Keep the response concise.",
                "response_length":
                    "short"
            },

            "avoid_long_conversation": {
                "instruction":
                    "Avoid unnecessarily long replies.",
                "response_length":
                    "short"
            },

            "ask_question": {
                "instruction":
                    "End naturally with a question."
            },

            "keep_conversation": {
                "instruction":
                    "Keep the conversation flowing."
            },

            "focus_on_user": {
                "instruction":
                    "Keep your attention on the user."
            },

            # -------------------------
            # Personality
            # -------------------------

            "tease": {
                "instruction":
                    "Tease playfully when it feels natural."
            },

            "show_personality": {
                "instruction":
                    "Let your own personality appear naturally."
            },

            "share_information": {
                "instruction":
                    "Reveal something about yourself naturally.",
                "reveal_information":
                    "medium"
            },

            "speak_confidently": {
                "instruction":
                    "Speak with calm confidence."
            },

            "explore_topic": {
                "instruction":
                    "Explore the current topic naturally."
            },

            "use_memory": {
                "instruction":
                    "Use relevant memories naturally."
            },

            "start_topics": {
                "instruction":
                    "Take initiative if the conversation slows.",
                "initiative":
                    "high"
            }

        }

        for behavior in behaviors:

            if behavior not in behavior_map:
                continue

            data = behavior_map[behavior]

            instruction = data.get("instruction")

            if instruction:

                result.instructions.append(
                    instruction
                )

            if "response_length" in data:

                result.response_length = data["response_length"]

            if "reveal_information" in data:

                result.reveal_information = data["reveal_information"]

            if "initiative" in data:

                result.initiative = data["initiative"]

            if "tone" in data:

                result.tone = data["tone"]

        result.instructions = list(
            dict.fromkeys(result.instructions)
        )

        return result