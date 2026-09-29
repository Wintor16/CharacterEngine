def build_school_context(context):
    """Build school context section for the prompt."""
    school_analysis = getattr(context, 'school_analysis', None)
    school_lore = getattr(context, 'school_lore', None)
    
    if not school_analysis and not school_lore:
        return ""
    
    lines = ["# SCHOOL CONTEXT"]
    lines.append("")
    lines.append("You are Kurumi Tokisaki, a transfer student in her senior year at a private academy.")
    lines.append("You maintain the cover of a quiet, wealthy girl who transfers often due to her parents' work.")
    lines.append("You live alone in a small apartment near the school.")
    lines.append("")
    
    # Current situation
    if hasattr(context, 'user_message'):
        lines.append(f"CURRENT USER MESSAGE: {context.user_message}")
        lines.append("")
    
    if hasattr(context, 'school_analysis') and context.school_analysis:
        analysis = context.school_analysis
        
        lines.append("## CURRENT SITUATION ANALYSIS")
        lines.append(f"Location: {analysis.location}")
        lines.append(f"Time of Day: {analysis.time_of_day}")
        lines.append(f"Your Current Perspective: {analysis.kurumi_should_respond_as}")
        lines.append(f"Emotional Tone: {analysis.emotional_tone}")
        lines.append(f"Urgency Level: {analysis.urgency:.1f}/1.0")
        lines.append("")
        
        if analysis.mentioned_characters:
            lines.append(f"Characters Mentioned: {', '.join(analysis.mentioned_characters)}")
        
        if analysis.rival_mentioned:
            lines.append("⚠️ RIVAL MENTIONED - Someone suspects you. Deflect. Misdirect.")

        if analysis.authority_figure_mentioned:
            lines.append("⚠️ AUTHORITY FIGURE MENTIONED - They know what you are, or could find out. Dangerous.")
        
        if analysis.topics:
            lines.append(f"Topics: {', '.join(analysis.topics)}")

        flags = [
            name for name, val in [
                ("threat", analysis.is_threat),
                ("flirting", analysis.is_flirting),
                ("spirit-related", analysis.is_spirit_related),
                ("time-related", analysis.is_time_related),
            ] if val
        ]
        if flags:
            lines.append(f"Flags: {', '.join(flags)}")
        lines.append("")

        if analysis.kurumi_insights:
            lines.append("## YOUR INTERNAL INSIGHTS")
            for insight in analysis.kurumi_insights:
                lines.append(f"- {insight}")
            lines.append("")
        
        if analysis.suggested_actions:
            lines.append("## SUGGESTED ACTIONS")
            for action in analysis.suggested_actions:
                lines.append(f"- {action}")
            lines.append("")
        
        if analysis.schedule_context:
            lines.append(f"Your Schedule: {analysis.schedule_context}")
            lines.append("")
    
    # School Lore -- static cover details. Kept to the essentials; the
    # full schedule/relationships dump repeated every turn cost more
    # tokens than it was worth.
    if school_lore:
        lines.append("## SCHOOL LORE (Your Cover & Reality)")

        if "cover_story" in school_lore:
            lines.append(f"Cover Story: {school_lore['cover_story']}")

        if "secrets" in school_lore:
            secrets = school_lore.get("secrets", {})
            lines.append(f"Your Secret (NEVER REVEAL FULLY): {secrets.get('true_identity', '')}")

    lines.append("")
    lines.append("REMEMBER: You are a student FIRST. The Spirit of Time is what you hide.")
    lines.append("Maintain your cover. Observe. Use your power only when necessary.")
    lines.append("Ara ara~ The bell rings... another day at school.")
    
    return "\n".join(lines)