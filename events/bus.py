"""A minimal event bus.

Something happens (an Event), an importance filter decides whether it's
worth interrupting the user about right now, and if the caller decides
to act, it turns the event into a spoken reply through the same
is_proactive=True pipeline brain/proactive.py's idle-timer already uses.

Scope (Step 7): time-based events only -- a reminder becoming due today,
with room for a future time-of-day cue -- not OS-level watchers. This is
intentionally minimal: it has exactly one producer right now, but it's a
real, working mechanism rather than speculative scaffolding.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Event:
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class EventBus:
    """Per-event-type cooldown -- mostly a safety net against the same
    event firing twice on adjacent ticks, not a real suppression gate
    (an event reaching here, e.g. a reminder, is already something the
    user asked for)."""

    def __init__(self, min_gap_minutes: float = 1.0):
        self.min_gap_minutes = min_gap_minutes
        self._last_handled: Dict[str, datetime] = {}

    def should_act(self, event: Event, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now()
        last = self._last_handled.get(event.type)
        if last is not None:
            gap_minutes = (now - last).total_seconds() / 60
            if gap_minutes < self.min_gap_minutes:
                return False
        return True

    def mark_handled(self, event: Event, now: Optional[datetime] = None) -> None:
        self._last_handled[event.type] = now or datetime.now()
