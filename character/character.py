from dataclasses import dataclass


@dataclass
class Character:
    identity: dict
    personality: dict
    speech: dict
    behavior: dict
    preferences: dict
    goals: dict
    rules: list
    mind: dict = None
    habits: dict = None
    school_lore: dict = None

    version: str = "1.0"

    @property
    def name(self):
        return self.identity.get("name", "Unknown")

    @property
    def description(self):
        return self.identity.get("description", "")

    def to_dict(self):
        return {
            "identity": self.identity,
            "personality": self.personality,
            "speech": self.speech,
            "behavior": self.behavior,
            "preferences": self.preferences,
            "goals": self.goals,
            "rules": self.rules,
            "mind": self.mind,
            "habits": self.habits,
            "school_lore": self.school_lore,
            "version": self.version,
        }