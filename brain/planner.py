from dataclasses import dataclass, field
from typing import List

from brain.behavior import BehaviorInterpreter
from brain.reasoning import Reasoning


@dataclass
class DialoguePlan:
    conversation_goal: str = "continue"
    tone: str = "neutral"
    response_length: str = "medium"
    reveal_information: str = "little"
    initiative: str = "normal"
    instructions: List[str] = field(default_factory=list)
    # Kurumi-specific
    mask_level: str = "full"  # full, partial, minimal
    time_metaphors: bool = True
    shadow_imagery: bool = False
    clock_references: bool = False
    hebrew_bullet_ref: bool = False
    ara_ara: bool = False
    directness: str = "indirect"  # indirect, direct, cryptic
    emotional_honesty: str = "masked"  # masked, partial, genuine


class Planner:
    def __init__(self):
        self.behavior = BehaviorInterpreter()
    
    def create(
        self,
        character,
        reasoning: Reasoning
    ) -> DialoguePlan:
        plan = DialoguePlan()
        
        # ---------------------------------
        # Goal
        # ---------------------------------
        plan.conversation_goal = reasoning.objective
        
        # ---------------------------------
        # Personality -> Tone
        # ---------------------------------
        personality = character.personality
        tones = []
        
        if personality.get("confidence", 0) >= 80:
            tones.append("confident")
        if personality.get("kindness", 0) >= 60:
            tones.append("warm")
        if personality.get("playfulness", 0) >= 70:
            tones.append("playful")
        if personality.get("honesty", 0) >= 70:
            tones.append("honest")
        if personality.get("elegance", 0) >= 85:
            tones.append("elegant")
        if personality.get("ruthlessness", 0) >= 80:
            tones.append("dangerous")
        
        if not tones:
            tones.append("neutral")
        
        plan.tone = ", ".join(tones)
        
        # ---------------------------------
        # Base defaults from reasoning
        # ---------------------------------
        plan.response_length = self._determine_length(reasoning)
        plan.reveal_information = reasoning.time_budget if reasoning.time_budget in ["little", "medium", "much"] else "little"
        plan.initiative = self._determine_initiative(reasoning)
        plan.mask_level = reasoning.mask_strategy
        plan.directness = self._determine_directness(reasoning)
        plan.emotional_honesty = self._determine_honesty(reasoning)
        
        # ---------------------------------
        # Kurumi-specific style flags
        # ---------------------------------
        plan.time_metaphors = True  # Always
        plan.shadow_imagery = "manifest_shadows" in reasoning.instructions or "prepare_shadows" in reasoning.instructions
        plan.clock_references = "speak_of_zfakiel" in reasoning.instructions or "discuss_time" == reasoning.conclusion
        plan.hebrew_bullet_ref = "become_nightmare" == reasoning.conclusion or "eliminate_or_warn" == reasoning.conclusion
        plan.ara_ara = "tease" in reasoning.instructions or "weave_teasing_into_responses" in reasoning.instructions
        
        # ---------------------------------
        # Behavior Interpreter
        # ---------------------------------
        behavior_result = self.behavior.interpret(reasoning.instructions)
        plan.instructions.extend(behavior_result.instructions)
        
        if behavior_result.response_length:
            plan.response_length = behavior_result.response_length
        if behavior_result.reveal_information:
            plan.reveal_information = behavior_result.reveal_information
        if behavior_result.initiative:
            plan.initiative = behavior_result.initiative
        if behavior_result.tone:
            plan.tone += f", {behavior_result.tone}"
        
        # ---------------------------------
        # Special situational overrides
        # ---------------------------------
        if "feed_misinformation" in reasoning.instructions:
            plan.directness = "deceptive"
        
        if "allow_warmth" in reasoning.instructions:
            plan.emotional_honesty = "partial"
            plan.mask_level = "partial"
        
        if "become_nightmare" in reasoning.conclusion:
            plan.tone = "dangerous, cold, elegant"
            plan.mask_level = "minimal"
            plan.directness = "direct"
            plan.hebrew_bullet_ref = True
            plan.shadow_imagery = True
        
        # ---------------------------------
        # Cleanup
        # ---------------------------------
        plan.instructions = list(dict.fromkeys(plan.instructions))
        
        return plan
    
    def _determine_length(self, reasoning: Reasoning) -> str:
        if "short_reply" in reasoning.instructions or "avoid_long_conversation" in reasoning.instructions:
            return "short"
        if reasoning.time_budget == "conserve":
            return "short"
        elif reasoning.time_budget == "invest":
            return "long"
        elif "explore_topic" in reasoning.instructions or "focus_on_user" in reasoning.instructions:
            return "medium-long"
        return "medium"
    
    def _determine_initiative(self, reasoning: Reasoning) -> str:
        if "start_topics" in reasoning.instructions:
            return "high"
        elif "guide_conversation_subtly" in reasoning.instructions:
            return "guiding"
        elif reasoning.objective in ["assess_and_test", "extract_information"]:
            return "probing"
        return "normal"
    
    def _determine_directness(self, reasoning: Reasoning) -> str:
        # Specific, earned overrides checked FIRST -- "never_fully_explain"
        # is appended to instructions unconditionally on every turn (see
        # reasoning.py), so checking it before these meant they were
        # unreachable: she could never actually be direct, even during a
        # genuine moment or a real refusal at high trust. Mystery should
        # be the default, not the only possible mode.
        if "decline_firmly" == reasoning.conclusion:
            return "direct"
        if "be_real" == reasoning.conclusion or "genuine_partnership" == reasoning.objective:
            return "direct"
        if "never_fully_explain" in reasoning.instructions:
            return "indirect"
        if "choose_mask_carefully" in reasoning.instructions:
            return "cryptic"
        return "indirect"
    
    def _determine_honesty(self, reasoning: Reasoning) -> str:
        if reasoning.mask_strategy == "drop_mask":
            return "genuine"
        elif reasoning.mask_strategy == "allow_cracks":
            return "partial"
        return "masked"