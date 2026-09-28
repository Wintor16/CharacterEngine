"""One-off reminders, persisted per character.

Storage follows brain/persistence.py's atomic-write pattern (tmp file +
Path.replace()) so a crash mid-write can't corrupt the file, but lives in
a separate file from BrainState since reminders aren't part of the
character's mood/relationship/needs.
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Reminder:
    id: str
    due_at: str  # ISO timestamp
    message: str
    created_at: str
    fired: bool = False


def _path(character_name: str) -> Path:
    safe_name = character_name.replace("/", "_")
    return PROJECT_ROOT / "data" / "state" / f"{safe_name}_reminders.json"


def _load(character_name: str) -> List[Reminder]:
    path = _path(character_name)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Reminder(**r) for r in data.get("reminders", [])]
    except Exception as e:
        print(f"[Scheduler] Failed to load reminders, starting fresh: {e}")
        return []


def _save(character_name: str, reminders: List[Reminder]) -> None:
    path = _path(character_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"reminders": [asdict(r) for r in reminders]}
    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


class ReminderScheduler:
    """One-off reminders for a single character, persisted to disk."""

    def __init__(self, character_name: str):
        self.character_name = character_name
        self._reminders = _load(character_name)

    def add(self, message: str, due_at: datetime) -> Reminder:
        reminder = Reminder(
            id=uuid.uuid4().hex[:8],
            due_at=due_at.isoformat(),
            message=message,
            created_at=datetime.now().isoformat(),
        )
        self._reminders.append(reminder)
        _save(self.character_name, self._reminders)
        return reminder

    def list_pending(self) -> List[Reminder]:
        return [r for r in self._reminders if not r.fired]

    def cancel(self, reminder_id: str) -> bool:
        before = len(self._reminders)
        self._reminders = [r for r in self._reminders if r.id != reminder_id]
        if len(self._reminders) != before:
            _save(self.character_name, self._reminders)
            return True
        return False

    def pop_due(self, now: Optional[datetime] = None) -> List[Reminder]:
        """Mark due, unfired reminders as fired and return them."""
        now = now or datetime.now()
        due = []
        for r in self._reminders:
            if not r.fired and datetime.fromisoformat(r.due_at) <= now:
                r.fired = True
                due.append(r)
        if due:
            _save(self.character_name, self._reminders)
        return due
