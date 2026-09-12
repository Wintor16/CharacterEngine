from dataclasses import dataclass
from typing import List, Optional

from brain.context import BrainContext
from brain.decision import DecisionMaker
from brain.emotion import EmotionEngine
from brain.needs import NeedsEngine
from brain.observation import Observer
from brain.perception import Perception
from brain.planner import Planner
from brain.reasoning import ReasoningEngine
from brain.relationship import RelationshipEngine
from brain.school_context import SchoolContextEngine
from brain.state import BrainState
from brain.state_updater import StateUpdater
from brain.thought import ThoughtGenerator
from memory.advanced_memory import AdvancedMemorySystem


@dataclass
class BrainResult:
    context: BrainContext


class Brain:
    def __init__(
        self,
        character,
        memory
    ):
        self.character = character
        self.memory = memory  # Legacy memory manager for backward compatibility
        
        # Advanced memory system
        self.advanced_memory = AdvancedMemorySystem(
            character_name=character.name,
            max_short_term=20,
            max_long_term=1000
        )
        
        self.state = BrainState()
        
        # Brain Systems
        self.perception = Perception()
        self.observer = Observer()
        self.decision = DecisionMaker()
        self.relationship = RelationshipEngine()
        self.emotion = EmotionEngine()
        self.needs = NeedsEngine()
        self.state_updater = StateUpdater()
        self.thought = ThoughtGenerator()
        self.reasoning = ReasoningEngine()
        self.planner = Planner()
        self.school_context = SchoolContextEngine(character)
        
        # Load school lore into character
        self._load_school_lore()

    def _load_school_lore(self):
        """Load school lore into character for brain access."""
        import json
        from pathlib import Path
        
        lore_path = Path("characters/kurumi/lore/school.json")
        if lore_path.exists():
            with open(lore_path, 'r', encoding='utf-8') as f:
                self.school_lore = json.load(f)
        else:
            self.school_lore = {}
        
        # Add school context to character
        self.character.school_lore = self.school_lore

    def process(
        self,
        user_message: str
    ) -> BrainResult:
        # Add user message to advanced memory
        self.advanced_memory.add_short_term("user", user_message)
        
        # ---------------------------------
        # Perception
        # ---------------------------------
        perception = self.perception.analyze(user_message)
        
        # ---------------------------------
        # School Context Analysis
        # ---------------------------------
        school_analysis = self.school_context.analyze(
            user_message, 
            self.state, 
            self.school_lore
        )
        
        # ---------------------------------
        # Observation
        # ---------------------------------
        observation = self.observer.observe(
            self.character,
            perception,
            self.state,
            school_analysis
        )
        
        # ---------------------------------
        # Memory Retrieval (Advanced)
        # ---------------------------------
        relevant_memories = self.advanced_memory.retrieve(user_message, limit=5)
        
        # Also get recent memories for context
        recent_memories = self.advanced_memory.get_recent_memories(hours=24, limit=10)
        
        # Combine memories for decision making
        all_memories = relevant_memories + recent_memories
        # Deduplicate
        seen_ids = set()
        unique_memories = []
        for m in all_memories:
            if m.id not in seen_ids:
                seen_ids.add(m.id)
                unique_memories.append(m)
        
        # Convert to legacy format for backward compatibility
        legacy_memories = []
        for m in unique_memories:
            legacy_memories.append(type('Memory', (), {
                'content': m.content,
                'importance': m.importance,
                'category': m.memory_type,
                'tags': m.tags,
                'emotion': str(m.emotional_valence)
            })())
        
        # ---------------------------------
        # Decision
        # ---------------------------------
        decision = self.decision.decide(
            self.character,
            observation,
            self.state,
            legacy_memories
        )
        
        # ---------------------------------
        # Relationship
        # ---------------------------------
        self.relationship.update(
            self.state.relationship,
            observation,
            decision
        )
        self.relationship.interpret(self.state.relationship)
        
        # ---------------------------------
        # Emotion
        # ---------------------------------
        emotion = self.emotion.update(
            decision,
            observation,
            self.state
        )
        self.emotion.interpret(emotion)
        
        # ---------------------------------
        # Needs
        # ---------------------------------
        self.needs.update(
            self.character,
            self.state.needs,
            observation,
            decision,
            emotion,
            self.state.relationship
        )
        self.needs.interpret(self.state.needs)
        
        # ---------------------------------
        # State
        # ---------------------------------
        self.state_updater.update(self.state, decision)
        
        # ---------------------------------
        # Thoughts
        # ---------------------------------
        thoughts = self.thought.generate(
            self.character,
            observation,
            decision,
            emotion,
            self.state.relationship,
            self.state.needs,
            unique_memories
        )
        
        # ---------------------------------
        # Reasoning
        # ---------------------------------
        reasoning = self.reasoning.process(
            self.character,
            observation,
            decision,
            emotion,
            self.state.relationship,
            self.state.needs,
            thoughts,
            self.state
        )
        
        # ---------------------------------
        # Planner
        # ---------------------------------
        plan = self.planner.create(self.character, reasoning)
        
        # ---------------------------------
        # Context
        # ---------------------------------
        context = BrainContext(
            state=self.state,
            observation=observation,
            decision=decision,
            emotion=emotion,
            relationship=self.state.relationship,
            needs=self.state.needs,
            thoughts=thoughts,
            reasoning=reasoning,
            plan=plan,
            memories=legacy_memories
        )
        
        # Add school context to context for prompt building
        context.school_analysis = school_analysis
        context.school_lore = self.school_lore
        context.advanced_memories = unique_memories
        
        # ---------------------------------
        # Store assistant response in advanced memory
        # ---------------------------------
        # This will be done after LLM generates response
        # We store it here for next turn
        context.user_message = user_message
        
        return BrainResult(context=context)
    
    def store_response(self, response_text: str):
        """Store assistant response in advanced memory."""
        self.advanced_memory.add_short_term("assistant", response_text)