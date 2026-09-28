"""
Memory Consolidation and Reflection System for Kurumi.

This module handles:
- Automatic memory formation from conversations
- Memory consolidation (merging similar memories)
- Reflection/inner monologue generation
- Emotional tagging of memories
- Importance decay over time
"""

from dataclasses import dataclass, field
from typing import List, Dict
import re

from memory.advanced_memory import AdvancedMemorySystem, Memory


@dataclass
class MemoryCandidate:
    """A potential memory extracted from conversation."""
    content: str
    category: str = "conversation"
    importance: float = 0.5
    emotion: str = ""
    tags: List[str] = field(default_factory=list)
    people: List[str] = field(default_factory=list)
    source_turn: int = 0


class MemoryConsolidator:
    """Consolidates conversation history into long-term memories."""

    # Maps a candidate's free-form trigger category to the four memory
    # types AdvancedMemorySystem indexes on. The original category is kept
    # as a tag, so nothing is lost by folding it into a coarser bucket.
    CATEGORY_TO_MEMORY_TYPE = {
        "personal_revelation": "semantic",
        "emotional_moment": "emotional",
        "intimacy": "emotional",
        "kurumi_specific": "episodic",
        "conflict": "episodic",
        "conversation": "episodic",
    }

    # Patterns that indicate memorable moments
    MEMORY_TRIGGERS = {
        "personal_revelation": [
            r"i (am|was|feel|felt|think|thought|believe|believed)",
            r"my (name|past|childhood|family|secret|dream|fear|goal)",
            r"i (want|need|hope|wish|dream) to",
        ],
        "emotional_moment": [
            r"(love|hate|fear|angry|sad|happy|joy|grief|loss|pain)",
            r"(cry|tears|laugh|smile|hug|kiss|embrace)",
            r"(betray|trust|promise|swear|vow)",
        ],
        "kurumi_specific": [
            r"(time|clock|bullet|zafkiel|shadow|nightmare|spirit)",
            r"(timeline|past|future|memory|remember|forget)",
            r"(ara ara|tick tock|time will tell)",
        ],
        "conflict": [
            r"(fight|battle|attack|defend|protect|kill|die|death)",
            r"(threat|danger|warning|enemy|foe|rival)",
            r"(disagree|argue|conflict|oppose|resist)",
        ],
        "intimacy": [
            r"(close|intimate|touch|hold|kiss|embrace|warmth)",
            r"(trust|open up|reveal|share|confide|secret)",
            r"(care|matter|important|special|dear|precious)",
        ]
    }
    
    def __init__(self, advanced_memory: AdvancedMemorySystem):
        self.advanced_memory = advanced_memory
        self.turn_counter = 0
        self.pending_candidates: List[MemoryCandidate] = []
    
    def process_conversation_turn(
        self,
        user_message: str,
        kurumi_response: str,
        brain_state=None,
        emotion=None
    ) -> List[Memory]:
        """Process a conversation turn and extract potential memories."""
        self.turn_counter += 1
        new_memories = []

        # Trigger matching AND the stored content itself are both based on
        # the USER's message only, not Kurumi's reply. Two reasons: (1)
        # her own dialogue is habitually flowery/emotionally-coded (that's
        # just her voice), so scoring against it too made almost every
        # exchange look "significant" and flooded memory with near-
        # duplicate small talk; (2) storing her exact past wording meant a
        # later retrieval would hand the model that verbatim text back as
        # a "memory", and -- true to this project's recurring finding that
        # a small model reproduces any quotable text placed in the prompt
        # -- it would just recite the old line for an unrelated question
        # instead of generating a real new response. kurumi_response is
        # deliberately unused here now.

        # Check for memory triggers
        candidates = self._extract_candidates(user_message, brain_state, emotion)
        
        for candidate in candidates:
            candidate.source_turn = self.turn_counter
            self.pending_candidates.append(candidate)
        
        # Consolidate if we have enough candidates
        if len(self.pending_candidates) >= 3:
            new_memories = self._consolidate_pending()
        
        # Also create memories for high-importance single moments
        for candidate in candidates:
            if candidate.importance >= 0.8:
                memory = self._store_candidate(candidate)
                new_memories.append(memory)
        
        return new_memories
    
    def _extract_candidates(
        self,
        user_message: str,
        brain_state,
        emotion
    ) -> List[MemoryCandidate]:
        """Extract memory candidates. Trigger matching runs against what the
        user said, not Kurumi's reply -- see process_conversation_turn."""
        candidates = []
        text_lower = user_message.lower()
        
        # Determine base importance from triggers
        max_importance = 0.3
        matched_categories = []
        
        for category, patterns in self.MEMORY_TRIGGERS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matched_categories.append(category)
                    if category == "kurumi_specific":
                        max_importance = max(max_importance, 0.7)
                    elif category in ["personal_revelation", "emotional_moment"]:
                        max_importance = max(max_importance, 0.6)
                    elif category in ["conflict", "intimacy"]:
                        max_importance = max(max_importance, 0.5)
        
        # Boost importance based on emotional state
        if emotion:
            if emotion.intensity >= 0.7:
                max_importance = max(max_importance, 0.6)
            if emotion.primary in ["complex", "touched", "intimidating"]:
                max_importance = max(max_importance, 0.7)
        
        # Boost based on relationship state
        if brain_state and hasattr(brain_state, 'relationship'):
            rel = brain_state.relationship
            if rel.trust > 50:
                max_importance = max(max_importance, 0.5)
            if rel.affection > 40:
                max_importance = max(max_importance, 0.6)
        
        # Only create candidate if importance is sufficient
        if max_importance >= 0.4:
            # Determine primary category
            primary_category = matched_categories[0] if matched_categories else "conversation"
            
            # Extract emotion tag
            emotion_tag = ""
            if emotion:
                emotion_tag = emotion.primary
                if emotion.secondary != "none":
                    emotion_tag += f"+{emotion.secondary}"
            
            # Extract tags
            tags = list(set(matched_categories))
            
            # Detect people mentioned (no hardcoded cast -- left empty
            # unless/until real named-entity detection is added)
            people = []

            # Store only what the user said, not Kurumi's reply -- see
            # process_conversation_turn for why.
            content = user_message[:500]
            
            candidates.append(MemoryCandidate(
                content=content,
                category=primary_category,
                importance=max_importance,
                emotion=emotion_tag,
                tags=tags,
                people=people
            ))
        
        return candidates
    
    def _consolidate_pending(self) -> List[Memory]:
        """Consolidate pending candidates into cohesive memories."""
        if not self.pending_candidates:
            return []
        
        # Group by category
        by_category: Dict[str, List[MemoryCandidate]] = {}
        for candidate in self.pending_candidates:
            if candidate.category not in by_category:
                by_category[candidate.category] = []
            by_category[candidate.category].append(candidate)
        
        new_memories = []
        
        for category, candidates in by_category.items():
            if len(candidates) >= 2:
                # Merge into a consolidated memory
                merged = self._merge_candidates(candidates)
                memory = self._store_candidate(merged)
                new_memories.append(memory)
            elif len(candidates) == 1 and candidates[0].importance >= 0.5:
                # Single strong candidate
                memory = self._store_candidate(candidates[0])
                new_memories.append(memory)
        
        # Clear processed candidates
        self.pending_candidates.clear()
        
        return new_memories
    
    def _merge_candidates(self, candidates: List[MemoryCandidate]) -> MemoryCandidate:
        """Merge multiple candidates into one consolidated memory."""
        # Weight by importance
        total_importance = sum(c.importance for c in candidates)
        
        # Combine content
        contents = [c.content for c in candidates]
        combined_content = " | ".join(contents[:3])  # Limit to 3 segments
        
        # Combine tags
        all_tags = []
        for c in candidates:
            all_tags.extend(c.tags)
        unique_tags = list(set(all_tags))
        
        # Combine people
        all_people = []
        for c in candidates:
            all_people.extend(c.people)
        unique_people = list(set(all_people))
        
        # Average importance with boost for consolidation
        avg_importance = total_importance / len(candidates)
        consolidated_importance = min(0.9, avg_importance + 0.1)
        
        # Determine dominant emotion
        emotions = [c.emotion for c in candidates if c.emotion]
        dominant_emotion = max(set(emotions), key=emotions.count) if emotions else ""
        
        return MemoryCandidate(
            content=combined_content,
            category=candidates[0].category,
            importance=consolidated_importance,
            emotion=dominant_emotion,
            tags=unique_tags,
            people=unique_people,
            source_turn=candidates[-1].source_turn
        )
    
    def _store_candidate(self, candidate: MemoryCandidate) -> Memory:
        """Persist a candidate as a long-term memory in the advanced memory system."""
        context = f"{candidate.category} - Turn {candidate.source_turn}"
        if candidate.emotion:
            context += f" ({candidate.emotion})"

        return self.advanced_memory.add_memory(
            content=candidate.content,
            memory_type=self.CATEGORY_TO_MEMORY_TYPE.get(candidate.category, "episodic"),
            importance=candidate.importance,
            tags=list(set(candidate.tags + [candidate.category])),
            related_entities=candidate.people,
            context=context,
        )
    
    def force_consolidation(self) -> List[Memory]:
        """Force consolidation of all pending candidates."""
        return self._consolidate_pending()


class ReflectionEngine:
    """Generates Kurumi's inner reflections and monologues."""
    
    REFLECTION_TEMPLATES = {
        "end_of_conversation": [
            "The conversation ends. The echoes fade. What did I learn? What did I reveal?",
            "Another moment stolen from Time. Was it worth the seconds spent?",
            "They leave. I remain. The clock ticks on. Always.",
        ],
        "trust_milestone": [
            "Trust... such a fragile thing. They've earned a fragment. How curious.",
            "The walls have cracks now. Not broken. Just... permeable. Interesting.",
            "To trust is to risk. To risk is to live. Or so the saying goes.",
        ],
        "threat_encountered": [
            "They threaten. They posture. They have no concept of what they face.",
            "Fools playing at heroism. Either way, they break.",
            "The Nightmare does not frighten. The Nightmare IS fear.",
        ],
        "kindness_received": [
            "Kindness without agenda. A rarity. A danger. A... comfort?",
            "They offer warmth. I should refuse. I should... accept?",
            "A moment of humanity. How troubling. How... necessary.",
        ],
        "time_pressure": [
            "The bullets dwindle. The clock cannot be stopped.",
            "Every conversation costs. Every second spends. The accounting is exact.",
            "Time is the only currency. I am running out of it.",
        ]
    }
    
    def __init__(self):
        self.reflection_history: List[str] = []
    
    def generate_reflection(
        self,
        trigger: str,
        brain_state=None,
        relationship=None,
        needs=None
    ) -> str:
        """Generate a reflection based on trigger and current state."""
        templates = self.REFLECTION_TEMPLATES.get(trigger, self.REFLECTION_TEMPLATES["end_of_conversation"])
        
        # Select template based on state
        import random
        base_reflection = random.choice(templates)
        
        # Add contextual detail
        context_details = []
        
        if brain_state:
            if brain_state.time_bullets_remaining < 6:
                context_details.append(f"Only {brain_state.time_bullets_remaining} bullets remain.")
            if brain_state.shadow_activity == "manifested":
                context_details.append("My shadows still stir from the encounter.")
        
        if relationship:
            if relationship.trust > 70:
                context_details.append("They've come further than most.")
            elif relationship.trust < 20:
                context_details.append("A stranger still. A variable unmeasured.")
        
        if needs:
            if needs.time_pressure > 80:
                context_details.append("The deadline approaches. Time grows short.")
        
        if context_details:
            reflection = base_reflection + " " + " ".join(context_details)
        else:
            reflection = base_reflection
        
        self.reflection_history.append(reflection)
        # Keep only last 50 reflections
        if len(self.reflection_history) > 50:
            self.reflection_history = self.reflection_history[-50:]
        
        return reflection
    
    def get_recent_reflections(self, count: int = 5) -> List[str]:
        """Get recent reflections."""
        return self.reflection_history[-count:]


class InnerMonologueGenerator:
    """Generates Kurumi's moment-to-moment inner monologue during conversation."""
    
    def __init__(self):
        self.monologue_history: List[str] = []
    
    def generate(
        self,
        user_message: str,
        kurumi_response: str,
        brain_state=None,
        emotion=None,
        decision_intent: str = ""
    ) -> str:
        """Generate inner monologue for current exchange."""
        monologue_parts = []
        
        # Analyze user message
        user_lower = user_message.lower()
        
        # Quick reactions
        if "love" in user_lower or "care" in user_lower:
            monologue_parts.append("*Such dangerous words. Do they know the weight?*")
        elif "time" in user_lower or "clock" in user_lower:
            monologue_parts.append("*They speak of my domain so casually.*")
        elif "?" in user_message:
            monologue_parts.append("*A question. Another piece on the board.*")
        
        # Reaction based on emotion
        if emotion:
            if emotion.primary == "intimidating":
                monologue_parts.append("*Good. Let them feel the predator's gaze.*")
            elif emotion.primary == "amused":
                monologue_parts.append("*Ara ara~ This one entertains me.*")
            elif emotion.primary == "touched":
                monologue_parts.append("*A crack... So small. So dangerous.*")
        
        # Reaction based on decision
        if decision_intent == "intimidate_threat":
            monologue_parts.append("*Show them the Nightmare. Just a glimpse.*")
        elif decision_intent == "genuine_conversation":
            monologue_parts.append("*Rare... to speak without calculation.*")
        
        # State-based
        if brain_state:
            if brain_state.time_bullets_remaining < 4:
                monologue_parts.append("*Time runs thin. Choose words like bullets.*")
            if brain_state.stress > 70:
                monologue_parts.append("*The pressure builds. Focus.*")
        
        monologue = " ".join(monologue_parts) if monologue_parts else "*...observing... calculating...*"
        
        self.monologue_history.append(monologue)
        if len(self.monologue_history) > 100:
            self.monologue_history = self.monologue_history[-100:]
        
        return monologue