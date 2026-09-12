import json
from pathlib import Path
from dataclasses import asdict

from memory.memory import Memory


class MemoryStorage:

    def __init__(
        self,
        file_path="memory/data.json"
    ):

        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    # ----------------------------------
    # Load
    # ----------------------------------

    def load(self) -> list[Memory]:

        if not self.file_path.exists():

            return []

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

        except Exception:

            return []

        memories = []

        for item in data:

            try:

                memories.append(
                    Memory(**item)
                )

            except Exception:
                continue

        return memories

    # ----------------------------------
    # Save
    # ----------------------------------

    def save(
        self,
        memories: list[Memory]
    ):

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(

                [

                    asdict(memory)

                    for memory in memories

                ],

                f,

                indent=4,

                ensure_ascii=False

            )