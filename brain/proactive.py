"""Proactive behavior gate (spec Phase 8).

EVENT -> RELEVANCE -> IMPORTANCE -> CURRENT CONTEXT -> KURUMI'S STATE
-> DECISION -> ACTION

There's no OS-level event bus yet (file/app watchers -- a separate,
bigger phase), so the EVENT this engine reacts to is simply "enough
idle time has passed since the last exchange." RELEVANCE/IMPORTANCE are
folded into a single interest score built from her actual relationship
and needs state, and the DECISION step is deliberately biased toward
silence -- per spec, silence must be a first-class, common outcome, not
a fallback. Passing every gate does not guarantee speech; there's still
a final weighted coin flip, so it doesn't feel mechanical or scheduled.
"""

import random
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from config import settings


@dataclass
class ProactiveDecision:
    should_speak: bool
    # A narrative cue for what's happening, NOT the line she'll say --
    # fed through the real engine (see desktop/app.py) so what she
    # actually says is genuinely generated from her current mood and
    # relationship, not picked from a fixed list. A canned message here
    # would be exactly the "faking it" this was built to avoid.
    occasion: str = ""
    reason: str = ""


class ProactiveEngine:
    def __init__(
        self,
        min_idle_minutes: float = settings.PROACTIVE_MIN_IDLE_MINUTES,
        min_gap_minutes: float = settings.PROACTIVE_MIN_GAP_MINUTES,
    ):
        self.min_idle_minutes = min_idle_minutes
        self.min_gap_minutes = min_gap_minutes
        self.last_proactive_at: Optional[datetime] = None

    def evaluate(self, state, last_interaction_at: Optional[datetime]) -> ProactiveDecision:
        now = datetime.now()

        # Hard anti-spam floor, independent of how often this is called.
        if self.last_proactive_at is not None:
            since_last = (now - self.last_proactive_at).total_seconds() / 60
            if since_last < self.min_gap_minutes:
                return ProactiveDecision(False, reason="cooldown")

        if last_interaction_at is None:
            return ProactiveDecision(False, reason="no interaction yet this session")

        idle_minutes = (now - last_interaction_at).total_seconds() / 60
        if idle_minutes < self.min_idle_minutes:
            return ProactiveDecision(False, reason="not idle long enough")

        interest = self._interest_score(state)
        if interest < 0.4:
            return ProactiveDecision(False, reason=f"no real reason to speak (score={interest:.2f})")

        # Even a good reason doesn't guarantee she acts on it.
        if random.random() > interest:
            return ProactiveDecision(False, reason=f"chose silence (score={interest:.2f})")

        occasion = self._pick_occasion(state, idle_minutes)
        self.last_proactive_at = now
        return ProactiveDecision(
            True, occasion=occasion,
            reason=f"score={interest:.2f}, idle={idle_minutes:.0f}m"
        )

    def _interest_score(self, state) -> float:
        """How much reason she has to reach out, from her own state --
        not from anything the user did. Low trust/affection means low
        score almost by construction, matching spec §3/§8."""
        rel = state.relationship
        needs = state.needs

        score = 0.0
        if rel.trust > 20:
            score += 0.2
        if rel.affection > 20:
            score += 0.3
        if needs.social < 30:
            score += 0.3
        if needs.curiosity > 60:
            score += 0.2
        return min(score, 1.0)

    def _pick_occasion(self, state, idle_minutes: float) -> str:
        """A scene-setting cue, not a line of dialogue -- what she'll
        actually say gets generated fresh by the real engine from this,
        the same way the CLI's own opening line ("*A presence manifests
        from the shadows...*") already kicks off organic dialogue rather
        than printing a fixed greeting."""
        rel = state.relationship
        if rel.affection > 40:
            occasions = [
                "*Time has passed in silence. Your thoughts keep drifting back to him, more than you'd like to admit.*",
                "*It's been a while since he last spoke to you. You find yourself wondering when he'll return.*",
            ]
        elif rel.trust > 30:
            occasions = [
                "*The silence has stretched on for a while now. You're a little bored, and he crosses your mind.*",
                "*Nothing has happened in some time. You wonder, idly, if he's still there.*",
            ]
        else:
            occasions = [
                "*A long quiet has passed. You're not sure why you're thinking about him at all.*",
                "*Time ticks by with no word from him. Mildly curious, you consider breaking the silence yourself.*",
            ]
        return random.choice(occasions)
