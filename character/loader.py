import json
from pathlib import Path

from config import settings

from .character import Character


class CharacterLoader:

    def __init__(self, root=None):
        self.root = Path(root) if root else settings.CHARACTERS_DIR

    def load(self, character_name: str) -> Character:
        path = self.root / f"{character_name}.json"

        if not path.exists():
            raise FileNotFoundError(f"Character '{character_name}' not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return Character(
            identity=data["identity"],
            personality=data["personality"],
            speech=data["speech"],
            behavior=data["behavior"],
            preferences=data["preferences"],
            goals=data["goals"],
            rules=data["rules"],
            mind=data.get("mind") or {},
            habits=data.get("habits") or {},
            school_lore=data.get("lore") or {},
            version=data.get("version", "1.0"),
        )
