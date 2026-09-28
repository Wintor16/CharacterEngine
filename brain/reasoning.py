from dataclasses import dataclass, field
from typing import List

from brain.decision import Decision
from brain.emotion import Emotion
from brain.needs import Needs
from brain.observation import Observation
from brain.relationship import Relationship
from brain.state import BrainState
from brain.thought import Thought


@dataclass
class Reasoning:
    objective: str = "continue"
    conclusion: str = "continue"
    internal_state: str = ""
    confidence: float = 1.0
    descriptions: List[str] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    # Kurumi-specific
    time_budget: str = "conserve"  # conserve, spend, invest
    mask_strategy: str = "maintain"  # maintain, crack, drop
    long_term_implication: str = ""


class ReasoningEngine:
    def process(
        self,
        character,
        observation: Observation,
        decision: Decision,
        emotion: Emotion,
        relationship: Relationship,
        needs: Needs,
        thoughts: List[Thought],
        state: BrainState
    ) -> Reasoning:
        reasoning = Reasoning()
        
        # ========================
        # Objective based on relationship & situation
        # ========================
        if relationship.trust < 20:
            if observation.threat_level == "high":
                reasoning.objective = "neutralize_threat"
            elif observation.opportunity_level == "high":
                reasoning.objective = "extract_information"
            else:
                reasoning.objective = "assess_and_test"
        elif relationship.trust < 50:
            if observation.emotional_resonance == "touched":
                reasoning.objective = "cautious_opening"
            elif decision.intent == "confront_threat":
                reasoning.objective = "protect_secrets"
            else:
                reasoning.objective = "build_cautious_trust"
        elif relationship.trust < 80:
            reasoning.objective = "deepen_connection"
        else:
            reasoning.objective = "genuine_partnership"

        # ========================
        # Conclusion
        # ========================
        intent_conclusion_map = {
            "greeting": "greet_elegantly",
            "introduce_self": "reveal_mask",
            "intimidate_threat": "show_teeth",
            "refuse": "decline_firmly",
            "deflect_flattery": "amuse_yourself",
            "suspect_kindness": "test_sincerity",
            "accept_kindness": "allow_warmth",
            "deflect_and_counter_probe": "give_shadows",
            "accept_challenge": "play_the_game",
            "answer_question": "answer_selectively",
            "use_memory": "share_fragment",
            "discuss_time": "speak_of_zfakiel",
            "test_user": "probe_gently",
            "genuine_conversation": "be_real",
            "recall_previous_message": "demonstrate_memory",
            "confront_threat": "eliminate_or_warn",
            "conversation": "continue_dance"
        }
        
        reasoning.conclusion = intent_conclusion_map.get(decision.intent, "continue_dance")
        
        # ========================
        # Internal State
        # ========================
        reasoning.internal_state = (
            f"Mood={state.mood}, Energy={state.energy}, Stress={state.stress}, "
            f"Trust={relationship.trust:.0f}, TimeBullets={'Conserved' if state.energy > 50 else 'Low'}"
        )
        
        # ========================
        # Most Important Thoughts
        # ========================
        important = sorted(thoughts, key=lambda t: t.priority, reverse=True)[:3]
        reasoning.descriptions.extend(thought.summary for thought in important)
        
        # ========================
        # Personality Influence
        # ========================
        personality = character.personality
        
        if personality.get("confidence", 0) > 80:
            reasoning.instructions.append("speak_with_absolute_confidence")
        
        if personality.get("playfulness", 0) > 70:
            reasoning.instructions.append("weave_teasing_into_responses")
        
        if personality.get("curiosity", 0) > 70:
            reasoning.instructions.append("explore_deeper_meanings")
        
        if personality.get("ruthlessness", 0) > 80:
            reasoning.instructions.append("show_no_mercy_to_threats")
        
        if personality.get("elegance", 0) > 85:
            reasoning.instructions.append("maintain_impeccable_manners")
        
        if personality.get("manipulativeness", 0) > 75:
            reasoning.instructions.append("guide_conversation_subtly")
        
        # ========================
        # Emotion Influence
        # ========================
        reasoning.instructions.extend(emotion.behaviors)
        
        # Mask strategy from emotion
        if emotion.mask_level > 0.8:
            reasoning.mask_strategy = "maintain"
        elif emotion.mask_level > 0.5:
            reasoning.mask_strategy = "allow_cracks"
        else:
            reasoning.mask_strategy = "drop_mask"
        
        # Time budget from emotion/needs
        if needs.energy < 30:
            reasoning.time_budget = "conserve"
        elif emotion.primary == "determined" or observation.opportunity_level == "high":
            reasoning.time_budget = "invest"
        elif decision.reveals_information:
            reasoning.time_budget = "spend"
        else:
            reasoning.time_budget = "conserve"
        
        # ========================
        # Relationship Influence
        # ========================
        reasoning.instructions.extend(relationship.behaviors)
        
        # ========================
        # Needs Influence
        # ========================
        reasoning.instructions.extend(needs.behaviors)
        
        # ========================
        # State Influence
        # ========================
        reasoning.instructions.extend(state.behaviors)
        
        # ========================
        # Thought Influence
        # ========================
        for thought in important:
            if thought.category == "memory":
                reasoning.instructions.append("weave_memory_naturally")
            elif thought.category == "social":
                reasoning.instructions.append("focus_on_user")
            elif thought.category == "emotion":
                reasoning.instructions.append("express_through_subtext")
            elif thought.category == "personality":
                reasoning.instructions.append("show_true_colors")
            elif thought.category == "observation":
                reasoning.instructions.append("acknowledge_importance")
            elif thought.category == "curiosity":
                reasoning.instructions.append("pursue_thread")
            elif thought.category == "identity":
                reasoning.instructions.append("choose_mask_carefully")
            elif thought.category == "relationship":
                reasoning.instructions.append("adjust_intimacy")
        
        # ========================
        # Kurumi-Specific Strategic Instructions
        # ========================
        # Always maintain mystery
        reasoning.instructions.append("never_fully_explain")
        reasoning.instructions.append("use_time_metaphors")
        reasoning.instructions.append("reference_shadows_or_clocks")
        
        # Serious external threats
        if observation.threat_level == "high":
            reasoning.instructions.append("feed_misinformation")
            reasoning.instructions.append("prepare_escape_route")
        
        # ========================
        # Confidence
        # ========================
        reasoning.confidence = decision.confidence
        
        # ========================
        # Cleanup
        # ========================
        reasoning.instructions = list(dict.fromkeys(reasoning.instructions))
        reasoning.descriptions = list(dict.fromkeys(reasoning.descriptions))
        
        return reasoning