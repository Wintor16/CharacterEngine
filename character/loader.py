import json
from pathlib import Path

from config import settings

from .character import Character


class CharacterLoader:

    def __init__(self, root=None):
        self.root = Path(root) if root else settings.CHARACTERS_DIR

    def _load_json(self, folder: Path, filename: str):
        path = folder / filename

        if not path.exists():
            # Return empty dict for optional files instead of raising
            if filename in ("mind.json", "habits.json", "lore/school.json"):
                return {}
            raise FileNotFoundError(f"Missing character file: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load(self, character_name: str) -> Character:

        folder = self.root / character_name

        if not folder.exists():
            raise FileNotFoundError(f"Character '{character_name}' not found.")

        # Load school lore
        school_lore = self._load_json(folder, "lore/school.json")

        return Character(
            identity=self._load_json(folder, "identity.json"),
            personality=self._load_json(folder, "personality.json"),
            speech=self._load_json(folder, "speech.json"),
            behavior=self._load_json(folder, "behavior.json"),
            preferences=self._load_json(folder, "preferences.json"),
            goals=self._load_json(folder, "goals.json"),
            rules=self._load_json(folder, "rules.json"),
            mind=self._load_json(folder, "mind.json"),
            habits=self._load_json(folder, "habits.json"),
            school_lore=school_lore,
        )