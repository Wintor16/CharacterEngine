def build_memories(context):
    """Build Kurumi's memories section."""
    memories = context.memories
    if not memories:
        return ""
    
    lines = [
        "# RELEVANT MEMORIES (Fragments of Time)",
        "These memories surfaced because they resonate with the current moment.",
        "Kurumi remembers everything. Every timeline. Every conversation.",
        "But she chooses what to acknowledge.",
        ""
    ]
    
    for memory in memories:
        # Only include the memory content naturally, no tags or metadata
        lines.append(f"- {memory.content}")
    
    lines.append("")
    lines.append("Only mention a memory if it NATURALLY fits the conversation.")
    lines.append("Do not force memories in. Treat each one as something that happened, not a")
    lines.append("line to repeat -- react to it fresh, in your own words, the way remembering")
    lines.append("something actually feels, never by restating it back the way it's written here.")
    lines.append("Memories are tools. Weapons. Comforts. Use them as Kurumi would.")
    lines.append("NEVER repeat memory metadata, tags, or formatting in your response.")
    
    return "\n".join(lines)