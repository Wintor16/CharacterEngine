def build_state(context):
    """Build Kurumi's internal state section."""
    state = context.state
    if state is None:
        return ""
    
    lines = [
        "# INTERNAL STATE",
        "",
        f"Current Mood: {state.mood}",
        f"Energy: {state.energy}/100",
        f"Focus: {state.focus}/100", 
        f"Stress: {state.stress}/100",
        f"Time Bullets Remaining: {state.time_bullets_remaining}/12",
        f"Shadow Activity: {state.shadow_activity}",
        f"Zafkiel Eye: {state.zafkiel_eye_state}",
        f"Timeline Stability: {state.current_timeline_stability:.0%}",
        f"Current Goal: {state.current_goal}",
        f"Current Action: {state.current_action}",
        ""
    ]
    
    if state.descriptions:
        lines.append("State Interpretation:")
        for desc in state.descriptions:
            lines.append(f"- {desc}")
        lines.append("")
    
    if state.behaviors:
        lines.append("Current Tendencies:")
        for behavior in state.behaviors:
            lines.append(f"- {behavior}")
        lines.append("")
    
    lines.append("These describe your internal condition. They guide your responses subtly.")
    lines.append("The Time Bullets represent your metaphysical reserves. Low = conserve.")
    lines.append("Shadow Activity: dormant=calm, stirring=alert, active=ready, manifested=combat.")
    lines.append("Zafkiel Eye: concealed=hidden, visible=revealed, glowing=power active.")
    
    return "\n".join(lines)