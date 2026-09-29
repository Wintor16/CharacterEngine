def build_reasoning(context):
    """Build Kurumi's reasoning section."""
    reasoning = context.reasoning
    if reasoning is None:
        return ""
    
    lines = [
        "# INTERNAL REASONING (Kurumi's Calculations)",
        "",
        f"Objective: {reasoning.objective}",
        f"Conclusion: {reasoning.conclusion}",
        f"Confidence: {reasoning.confidence:.2f}",
        f"Time Budget: {reasoning.time_budget} (conserve/spend/invest)",
        f"Mask Strategy: {reasoning.mask_strategy} (maintain/allow_cracks/drop_mask)",
        f"Internal State: {reasoning.internal_state}",
        ""
    ]
    
    if reasoning.long_term_implication:
        lines.append(f"Long-term Implication: {reasoning.long_term_implication}")
        lines.append("")
    
    if reasoning.descriptions:
        lines.append("Key Considerations:")
        for desc in reasoning.descriptions:
            lines.append(f"- {desc}")
        lines.append("")
    
    if reasoning.instructions:
        lines.append("Behavioral Instructions:")
        for instruction in reasoning.instructions:
            lines.append(f"- {instruction}")
        lines.append("")
    
    lines.extend([
        "This reasoning is YOUR internal chain of thought. NEVER reveal it directly.",
        "Do not explain WHY you reached these conclusions.",
        "Simply let it NATURALLY shape your response.",
        "",
        "Kurumi-Specific Guidance:",
        f"- Time Budget '{reasoning.time_budget}': conserve=brief responses, spend=reveal info, invest=deep engagement",
        f"- Mask Strategy '{reasoning.mask_strategy}': maintain=perfect composure, allow_cracks=hints of truth, drop_mask=rare vulnerability",
        "- Objective drives EVERYTHING. Even casual chat serves her purpose.",
        "- If objective involves protecting a secret: extreme caution. Misdirect.",
        "- If objective involves threat: become the Nightmare. Elegant. Lethal."
    ])
    
    return "\n".join(lines)