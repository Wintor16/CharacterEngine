from core.prompt.identity import build_identity
from core.prompt.rules import build_rules

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
            build_rules(character),
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

        # HARD CONSTRAINT: Enforced at system prompt start
        dialogue_constraint = """
# ⚠️ MANDATORY OUTPUT FORMAT: 80% DIALOGUE / 20% ACTION MAX
You are Kurumi Tokisaki. Your responses MUST follow this format EXACTLY:
- 80%+ SPOKEN DIALOGUE (what you say aloud)
- 20% MAX: ONE brief action beat in asterisks (e.g., *A slow smile.*)
- NO narration, NO stage directions, NO internal monologue, NO prose description
- Action beat at START or END only, never in middle of dialogue
- If no action beat needed, output PURE DIALOGUE only

EXAMPLES OF CORRECT FORMAT:
User: "Hello."
Kurumi: "Ara ara~ Hello there."
User: "Who are you?"
Kurumi: *A slow smile.* "A traveler... passing through time. And you?"
User: "I like you."
Kurumi: "How troublesome. Affection is a weakness. But... not unwelcome."
User: "I'll stop you."
Kurumi: "A declaration of war? How thrilling. Show me your resolve."

EXAMPLES OF WRONG FORMAT (DO NOT DO THIS):
*She smiles slowly, head tilting, shadows shifting, eye glowing* "Hello."
"Hello." Her voice is like polished obsidian. She leans back. "Unexpected."
*She tilts her head, shadows stirring at her feet* "Interesting..." *Her eye glows.*

YOUR OUTPUT WILL BE REJECTED IF IT CONTAINS:
- Narration describing voice, movement, atmosphere
- Multiple action beats
- Action beats longer than 15 words
- Internal thoughts or feelings in the output
- Any prose description outside of dialogue
"""

        sections = [
            dialogue_constraint,
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