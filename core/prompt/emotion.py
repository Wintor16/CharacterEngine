def build_emotion(context):
    """Build Kurumi's emotional state section."""
    emotion = context.emotion
    if emotion is None:
        return ""
    
    lines = [
        "# EMOTIONAL STATE",
        "",
        f"Primary Emotion: {emotion.primary}",
        f"Intensity: {emotion.intensity:.2f}",
        f"Mask Level: {emotion.mask_level:.0%} (how much you hide)",
    ]
    
    if emotion.secondary != "none":
        lines.append(f"Secondary Emotion: {emotion.secondary} ({emotion.secondary_intensity:.2f})")
    
    if emotion.true_feeling:
        lines.append(f"True Feeling (HIDDEN): {emotion.true_feeling}")
    
    lines.append("")
    
    if emotion.descriptions:
        lines.append("Emotional Interpretation:")
        for desc in emotion.descriptions:
            lines.append(f"- {desc}")
        lines.append("")
    
    if emotion.behaviors:
        lines.append("Emotional Tendencies:")
        for behavior in emotion.behaviors:
            lines.append(f"- {behavior}")
        lines.append("")
    
    lines.append("These emotions should NATURALLY influence your wording, reactions, and decisions.")
    lines.append("High mask level = perfect composure. Low mask = cracks show.")
    lines.append("True Feeling is what YOU feel. Mask is what YOU SHOW. They can differ.")
    lines.append("Kurumi's primary emotion is often a performance. The secondary/true is real.")
    
    return "\n".join(lines)