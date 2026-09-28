"""Persists BrainState (mood, relationship, needs, ...) across restarts.

Without this, trust/affection/mood reset to defaults every launch, which
defeats the "earned relationship" premise of the character. See
AUDIT_AND_PLAN.md 2.3.
"""

import json
from dataclasses import asdict, fields
from datetime import datetime
from pathlib import Path
from typing import Optional

from brain.needs import Needs
from brain.relationship import Relationship
from brain.state import BrainState

STATE_SCHEMA_VERSION = 1

# Anchored to the project root regardless of the process's working
# directory, so autostart/desktop launches don't silently lose state.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _state_path(character_name: str) -> Path:
    safe_name = character_name.replace("/", "_")
    return PROJECT_ROOT / "data" / "state" / f"{safe_name}.json"


def _filtered(cls, data: dict) -> dict:
    """Keep only keys that are real fields of `cls`, so an older or newer
    save file never crashes the constructor."""
    known = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in known}


def save_state(character_name: str, state: BrainState) -> None:
    """Write state atomically (tmp file + rename) so a crash mid-write
    can't corrupt the saved state."""
    path = _state_path(character_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": STATE_SCHEMA_VERSION,
        "saved_at": datetime.now().isoformat(),
        "state": asdict(state),
    }

    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


def load_state(character_name: str) -> Optional[BrainState]:
    """Return the saved BrainState, or None if there isn't one / it can't
    be read (in which case the caller falls back to fresh defaults)."""
    path = _state_path(character_name)
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        data = payload.get("state", payload)

        relationship = Relationship(**_filtered(Relationship, data.get("relationship") or {}))
        needs = Needs(**_filtered(Needs, data.get("needs") or {}))

        rest = _filtered(BrainState, data)
        rest["relationship"] = relationship
        rest["needs"] = needs

        return BrainState(**rest)
    except Exception as e:
        print(f"[State persistence] Failed to load saved state, starting fresh: {e}")
        return None


def reset_state(character_name: str) -> None:
    """Delete the saved state file, if any (user-triggered reset, spec §25)."""
    path = _state_path(character_name)
    if path.exists():
        path.unlink()
