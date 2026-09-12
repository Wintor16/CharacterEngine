import json
from pathlib import Path


LORE_DIR = Path("character/lore")


def _load(name: str):

    path = LORE_DIR / f"{name}.json"

    if not path.exists():
        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def _write(lines, title, data):

    if not data:
        return

    lines.append(f"# {title}")

    if isinstance(data, dict):

        for key, value in data.items():

            if isinstance(value, list):

                lines.append(f"{key}:")

                for item in value:

                    lines.append(
                        f"- {item}"
                    )

            else:

                lines.append(
                    f"{key}: {value}"
                )

    elif isinstance(data, list):

        for item in data:

            lines.append(
                f"- {item}"
            )

    lines.append("")


def build_lore():

    lines = []

    _write(
        lines,
        "World",
        _load("world")
    )

    _write(
        lines,
        "History",
        _load("history")
    )

    _write(
        lines,
        "Daily Life",
        _load("daily_life")
    )

    _write(
        lines,
        "Knowledge",
        _load("knowledge")
    )

    _write(
        lines,
        "Relationships",
        _load("relationships")
    )

    _write(
        lines,
        "Worldview",
        _load("worldview")
    )

    lines.append(
        "Everything above is part of your lived experience."
    )

    lines.append(
        "Do not explain it unless it naturally comes up."
    )

    return "\n".join(lines)