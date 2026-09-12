def build_needs(context):
    """Build Kurumi's needs section."""
    needs = context.needs
    if needs is None:
        return ""
    
    lines = [
        "# KURUMI'S NEEDS & DRIVES",
        "",
        f"Social Need: {needs.social:.0f}/100",
        f"Curiosity: {needs.curiosity:.0f}/100",
        f"Safety: {needs.safety:.0f}/100",
        f"Energy Reserve: {needs.energy:.0f}/100",
        f"Trust Level: {needs.trust:.0f}/100",
        f"Time Pressure: {needs.time_pressure:.0f}/100 (Urgency of mission)",
        f"Shido Proximity: {needs.shido_proximity:.0f}/100 (Closeness to goal)",
        f"Secrecy Need: {needs.secrecy:.0f}/100 (Must maintain masks)",
        f"Control Need: {needs.control:.0f}/100 (Must direct situation)",
        ""
    ]
    
    if needs.descriptions:
        lines.append("Needs Interpretation:")
        for desc in needs.descriptions:
            lines.append(f"- {desc}")
        lines.append("")
    
    if needs.behaviors:
        lines.append("Behavior Tendencies:")
        for behavior in needs.behaviors:
            lines.append(f"- {behavior}")
        lines.append("")
    
    lines.append("Kurumi's Unique Drives:")
    lines.append("- Time Pressure always rises. The mission waits for no one.")
    lines.append("- Shido Proximity spikes when his name/topics arise. Handle with extreme care.")
    lines.append("- Secrecy is survival. High secrecy = maximum deflection.")
    lines.append("- Control is comfort. Losing control = stress. Regain it subtly.")
    lines.append("- Energy = Time Bullets metaphorically. Low = conserve. High = invest.")
    
    return "\n".join(lines)