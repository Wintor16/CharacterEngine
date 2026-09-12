def build_rules(character):

    rules = character.rules

    if not rules:
        return ""

    lines = [
        "# Character Rules"
    ]

    for rule in rules:
        lines.append(
            f"- {rule}"
        )

    return "\n".join(lines)
