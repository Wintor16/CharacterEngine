from .loader import CharacterLoader
from .character import Character


class CharacterManager:

    def __init__(self):
        self.loader = CharacterLoader()
        self.current: Character | None = None

    def load(self, name: str) -> Character:
        self.current = self.loader.load(name)
        return self.current

    @property
    def character(self) -> Character:
        if self.current is None:
            raise RuntimeError("No character loaded.")
        return self.current