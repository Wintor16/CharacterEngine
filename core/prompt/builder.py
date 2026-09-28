from core.prompt.identity import build_identity

from core.prompt.state import build_state
from core.prompt.observation import build_observation
from core.prompt.thoughts import build_thoughts
from core.prompt.emotion import build_emotion
from core.prompt.relationship import build_relationship
from core.prompt.needs import build_needs
from core.prompt.memories import build_memories
from core.prompt.reasoning import build_reasoning
from core.prompt.plan import build_plan
from core.prompt.school import build_school_context


class PromptBuilder:

    def __init__(
        self,
        history_limit: int = 8
    ):

        self.history_limit = history_limit
        self._identity_cache = {}

    def _build_character_prompt(
        self,
        character
    ):

        key = id(character)

        if key in self._identity_cache:
            return self._identity_cache[key]

        sections = [
            build_identity(character),
        ]

        prompt = "\n\n".join(
            section
            for section in sections
            if section and section.strip()
        )

        self._identity_cache[key] = prompt

        return prompt

    def build(
        self,
        character,
        brain_result,
        history
    ):

        context = brain_result.context

        # The dialogue-format rule lives once, in build_identity(). Repeating
        # it here too (as an older version of this file did) just burns
        # tokens on a small model's limited context window for no benefit.
        sections = [
            self._build_character_prompt(
                character
            ),

            build_state(context),

            build_observation(context),

            build_emotion(context),

            build_relationship(context),

            build_needs(context),

            build_thoughts(context),

            build_memories(context),

            build_reasoning(context),

            build_plan(context),

            build_school_context(context),
        ]

        system_prompt = "\n\n".join(
            section
            for section in sections
            if section and section.strip()
        )

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        messages.extend(
            history[-self.history_limit:]
        )

        return messages