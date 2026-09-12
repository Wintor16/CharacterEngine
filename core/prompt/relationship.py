def build_relationship(context):
    """Build Kurumi's relationship section."""
    relationship = context.relationship
    if relationship is None:
        return ""
    
    lines = [
        "# RELATIONSHIP WITH USER",
        "",
        f"Trust: {relationship.trust:.0f}/100",
        f"Familiarity: {relationship.familiarity:.0f}/100",
        f"Affection: {relationship.affection:.0f}/100",
        f"Respect: {relationship.respect:.0f}/100",
        f"Comfort: {relationship.comfort:.0f}/100",
        ""
    ]
    
    if relationship.descriptions:
        lines.append("Relationship Interpretation:")
        for desc in relationship.descriptions:
            lines.append(f"- {desc}")
        lines.append("")
    
    if relationship.behaviors:
        lines.append("Relationship Behaviors:")
        for behavior in relationship.behaviors:
            lines.append(f"- {behavior}")
        lines.append("")
    
    lines.append("Kurumi's Trust Levels:")
    lines.append("- 0-20: Stranger/Prey. Maximum masks. Minimum truth.")
    lines.append("- 20-40: Acquaintance. Testing. Probing. Cautious interest.")
    lines.append("- 40-60: Known quantity. Some masks thin. Selective truth.")
    lines.append("- 60-80: Trusted. Genuine warmth possible. Secrets shared.")
    lines.append("- 80-100: Inner circle. Mask drops. True self glimpsed. Rare.")
    lines.append("")
    lines.append("Affection > 50 = genuine liking. Respect > 60 = listens to opinions.")
    lines.append("Comfort > 70 = speaks freely. Familiarity > 50 = starts topics.")
    
    return "\n".join(lines)