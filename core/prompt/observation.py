def build_observation(context):
    """Build Kurumi's observation section."""
    observation = context.observation
    if observation is None:
        return ""
    
    lines = [
        "# CURRENT OBSERVATION",
        "This is what you currently perceive about the conversation.",
        ""
    ]
    
    if observation.kurumi_insights:
        lines.append("Kurumi's Insights (Your Internal Analysis):")
        for insight in observation.kurumi_insights:
            lines.append(f"- {insight}")
        lines.append("")
    
    if observation.descriptions:
        lines.append("Observations:")
        for desc in observation.descriptions:
            lines.append(f"- {desc}")
        lines.append("")
    
    if observation.facts:
        lines.append("Facts:")
        for fact in observation.facts:
            lines.append(f"- {fact}")
        lines.append("")
    
    lines.append(f"Importance: {observation.importance:.2f}")
    lines.append(f"Threat Level: {observation.threat_level}")
    lines.append(f"Opportunity Level: {observation.opportunity_level}")
    lines.append(f"Emotional Resonance: {observation.emotional_resonance}")
    lines.append("")
    
    lines.append("Treat these observations as YOUR OWN understanding of the situation.")
    lines.append("Kurumi's Insights are your private thoughts - NEVER speak them aloud directly.")
    lines.append("They inform your tone, your choices, your masked responses.")
    lines.append("Threat Level dictates caution. Opportunity dictates engagement.")
    
    return "\n".join(lines)