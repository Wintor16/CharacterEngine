import time
from datetime import datetime
from typing import Optional

from brain.brain import Brain
from config import settings
from core.llm import LLM
from core.prompt.builder import PromptBuilder
from memory.manager import MemoryManager
from memory.consolidation import MemoryConsolidator, ReflectionEngine, InnerMonologueGenerator


class CharacterEngine:
    def __init__(
        self,
        character,
        model: str = settings.MODEL
    ):
        self.character = character

        self.memory = MemoryManager(
            short_memory_limit=settings.HISTORY_LIMIT,
            character_name=character.name
        )

        self.brain = Brain(
            character=self.character,
            memory=self.memory
        )

        self.prompt_builder = PromptBuilder(
            history_limit=settings.HISTORY_LIMIT
        )

        self.llm = LLM(model=model)

        # Memory consolidation and reflection systems
        self.consolidator = MemoryConsolidator(self.brain.advanced_memory)
        self.reflection_engine = ReflectionEngine()
        self.monologue_generator = InnerMonologueGenerator()
        
        # Conversation tracking
        self.conversation_turn = 0
        self.session_start_time = time.time()
        # Only ever set from a real user message (see reply() below) --
        # a proactive message from her own side must never reset this,
        # or the idle-time gate in brain/proactive.py would never fire.
        self.last_interaction_at: Optional[datetime] = None
        # Structured, non-chain-of-thought metadata from the last turn --
        # see spec §11/§21: debug info is fine, hidden reasoning is not.
        self.last_debug: dict = {}

    def reply(
        self,
        user_message: str,
        is_proactive: bool = False,
        **llm_kwargs
    ):
        total_start = time.perf_counter()
        # Nothing else bounds a single message's length -- HISTORY_LIMIT
        # only caps how many past turns stay in context. Truncate rather
        # than reject so an overly long paste still gets a real reply.
        if len(user_message) > settings.MAX_MESSAGE_CHARS:
            user_message = user_message[:settings.MAX_MESSAGE_CHARS]

        # A proactive utterance (she speaks up on her own -- see
        # brain/proactive.py) must NOT count as "the user interacted,"
        # or it would reset her own idle clock and the idle-time gate
        # that triggered it would never fire again afterward.
        if not is_proactive:
            self.last_interaction_at = datetime.now()

        # ---------------------------------
        # Brain Processing
        # ---------------------------------
        brain_start = time.perf_counter()
        brain_result = self.brain.process(user_message)
        brain_time = time.perf_counter() - brain_start

        # ---------------------------------
        # User Message to Short-term Memory
        # ---------------------------------
        self.memory.add_message("user", user_message)

        # ---------------------------------
        # Build Prompt
        # ---------------------------------
        prompt_start = time.perf_counter()
        messages = self.prompt_builder.build(
            character=self.character,
            brain_result=brain_result,
            history=self.memory.conversation()
        )
        prompt_time = time.perf_counter() - prompt_start

        # ---------------------------------
        # LLM Generation
        # ---------------------------------
        llm_start = time.perf_counter()
        
        # Pass response_length from plan to LLM for token limit
        plan_response_length = "medium"
        if brain_result.context and brain_result.context.plan:
            plan_response_length = brain_result.context.plan.response_length
        
        response = self.llm.generate(
            messages, 
            response_length=plan_response_length,
            **llm_kwargs
        )
        llm_time = time.perf_counter() - llm_start

        # ---------------------------------
        # Post-Processing
        # ---------------------------------
        if response.success:
            # Add to short-term memory
            self.memory.add_message("assistant", response.text)
            self.brain.store_response(response.text)

            # Track conversation turn
            self.conversation_turn += 1
            
            # Memory Consolidation
            try:
                brain_state = brain_result.context.state if brain_result.context else None
                emotion = brain_result.context.emotion if brain_result.context else None
                
                new_memories = self.consolidator.process_conversation_turn(
                    user_message=user_message,
                    kurumi_response=response.text,
                    brain_state=brain_state,
                    emotion=emotion
                )
                if new_memories:
                    print(f"\n[Memory Consolidated: {len(new_memories)} new long-term memories formed]")
            except Exception as e:
                print(f"\n[Memory consolidation error: {e}]")
            
            # Generate inner monologue (for debugging/display)
            try:
                decision_intent = ""
                if brain_result.context and brain_result.context.decision:
                    decision_intent = brain_result.context.decision.intent
                
                monologue = self.monologue_generator.generate(
                    user_message=user_message,
                    kurumi_response=response.text,
                    brain_state=brain_state,
                    emotion=emotion,
                    decision_intent=decision_intent
                )
                # Store monologue in brain state for potential use
                if brain_state:
                    brain_state.last_monologue = monologue
            except Exception as e:
                print(f"\n[Monologue generation error: {e}]")

        # ---------------------------------
        # Performance Logging
        # ---------------------------------
        total_time = time.perf_counter() - total_start

        print(
            "\n[Performance]"
            f"\n  Brain      : {brain_time:.3f}s"
            f"\n  Prompt     : {prompt_time:.3f}s"
            f"\n  LLM        : {llm_time:.3f}s"
            f"\n  Total      : {total_time:.3f}s"
            f"\n  Turn       : #{self.conversation_turn}"
        )

        # ---------------------------------
        # Debug metadata (structured, not chain-of-thought -- spec §11/§21)
        # ---------------------------------
        ctx = brain_result.context
        self.last_debug = {
            "model": self.llm.model,
            "success": response.success,
            "timing": {
                "brain": round(brain_time, 3),
                "prompt": round(prompt_time, 3),
                "llm": round(llm_time, 3),
                "total": round(total_time, 3),
            },
            "prompt_chars": sum(len(m.get("content", "")) for m in messages),
            "decision_intent": ctx.decision.intent if ctx and ctx.decision else "",
            "decision_reason": ctx.decision.reason if ctx and ctx.decision else "",
            "emotion": ctx.emotion.primary if ctx and ctx.emotion else "",
            "emotion_intensity": round(ctx.emotion.intensity, 2) if ctx and ctx.emotion else 0.0,
            "reasoning_objective": ctx.reasoning.objective if ctx and ctx.reasoning else "",
            "plan_tone": ctx.plan.tone if ctx and ctx.plan else "",
            "plan_length": ctx.plan.response_length if ctx and ctx.plan else "",
            "memories_used": len(ctx.memories) if ctx and ctx.memories else 0,
        }

        return response

    def reset_everything(self):
        """Full reset: mood/relationship/needs, long-term memory, and the
        persisted conversation log are all wiped. Irreversible -- callers
        (the desktop tray button, CLI --reset-state) are expected to
        confirm with the user first."""
        self.brain.reset()
        self.memory.short_memory.clear()
        self.conversation_turn = 0
        self.session_start_time = time.time()
        self.last_interaction_at = None

    def end_conversation(self) -> str:
        """Call when conversation ends to generate final reflection."""
        # Force any pending memory consolidation
        final_memories = self.consolidator.force_consolidation()
        if final_memories:
            print(f"\n[Final consolidation: {len(final_memories)} memories saved]")
        
        # Generate end-of-conversation reflection
        brain_state = self.brain.state if hasattr(self.brain, 'state') else None
        relationship = brain_state.relationship if brain_state else None
        needs = brain_state.needs if brain_state else None
        
        reflection = self.reflection_engine.generate_reflection(
            trigger="end_of_conversation",
            brain_state=brain_state,
            relationship=relationship,
            needs=needs
        )
        
        return reflection

    def get_stats(self) -> dict:
        """Get current engine statistics."""
        brain_state = self.brain.state if hasattr(self.brain, 'state') else None
        
        stats = {
            "conversation_turn": self.conversation_turn,
            "session_duration": time.time() - self.session_start_time,
            "short_term_messages": len(self.memory.conversation()),
            "long_term_memories": len(self.brain.advanced_memory.long_term),
        }
        
        if brain_state:
            stats.update({
                "mood": brain_state.mood,
                "energy": brain_state.energy,
                "stress": brain_state.stress,
                "time_bullets": brain_state.time_bullets_remaining,
                "shadows": brain_state.shadow_activity,
                "trust": brain_state.relationship.trust,
                "affection": brain_state.relationship.affection,
            })
        
        return stats