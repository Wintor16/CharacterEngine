from brain.decision import Decision
from brain.state import BrainState


class StateUpdater:
    def update(self, state: BrainState, decision: Decision) -> BrainState:
        # -------------------------
        # Mood from decision
        # -------------------------
        intent_mood_map = {
            "greeting": "pleasant",
            "introduce_self": "confident",
            "intimidate_threat": "cold",
            "refuse": "cold",
            "deflect_flattery": "amused",
            "suspect_kindness": "wary",
            "accept_kindness": "touched",
            "deflect_and_counter_probe": "cold",
            "accept_challenge": "playful",
            "answer_question": "neutral",
            "use_memory": "nostalgic",
            "discuss_time": "determined",
            "test_user": "amused",
            "genuine_conversation": "pleasant",
            "confront_threat": "intimidating",
            "recall_previous_message": "thoughtful",
            "conversation": "neutral"
        }
        state.mood = intent_mood_map.get(decision.intent, "neutral")
        
        # -------------------------
        # Energy drain
        # -------------------------
        energy_cost = 1
        if decision.intent in ["confront_threat", "become_nightmare"]:
            energy_cost = 5
        elif decision.intent in ["intimidate_threat", "accept_kindness", "deflect_and_counter_probe", "accept_challenge"]:
            energy_cost = 3
        elif decision.reveals_information:
            energy_cost = 2
        
        state.energy = max(0, state.energy - energy_cost)
        
        # Time bullets metaphorical tracking
        if decision.time_cost > 0:
            state.time_bullets_remaining = max(0, state.time_bullets_remaining - decision.time_cost)
        
        # -------------------------
        # Stress
        # -------------------------
        stress_change = 0
        if decision.risk_level == "high":
            stress_change = 10
        elif decision.risk_level == "moderate":
            stress_change = 5
        elif decision.intent in ["accept_kindness", "genuine_conversation"]:
            stress_change = -5  # Reducing stress through connection
        
        state.stress = max(0, min(100, state.stress + stress_change))
        
        # -------------------------
        # Focus
        # -------------------------
        if decision.intent in ["confront_threat", "discuss_time"]:
            state.focus = min(100, state.focus + 10)
        elif decision.intent in ["conversation", "greeting"]:
            state.focus = max(0, state.focus - 2)
        
        # -------------------------
        # Current goal/action
        # -------------------------
        intent_goal_map = {
            "greeting": "Establish presence.",
            "introduce_self": "Present a mask.",
            "intimidate_threat": "Demonstrate why I am called Nightmare.",
            "refuse": "Make clear that orders don't work on her.",
            "deflect_flattery": "Amuse myself at their expense.",
            "suspect_kindness": "Test the steel beneath the silk.",
            "accept_kindness": "Allow a moment of humanity.",
            "deflect_and_counter_probe": "Turn the hunter into the hunted.",
            "accept_challenge": "Play the game. Win the game.",
            "answer_question": "Satisfy curiosity. Reveal nothing vital.",
            "use_memory": "Let the past serve the present.",
            "discuss_time": "Speak of Zafkiel's domain.",
            "test_user": "Measure their worth.",
            "genuine_conversation": "Enjoy a rare equality.",
            "confront_threat": "Eliminate the threat. Protect what's mine.",
            "recall_previous_message": "Demonstrate perfect recall.",
            "conversation": "Observe. Learn. Wait."
        }
        state.current_goal = intent_goal_map.get(decision.intent, "Continue the dance.")

        intent_action_map = {
            "greeting": "Exchanging pleasantries with a stranger.",
            "introduce_self": "Weaving a new identity.",
            "intimidate_threat": "Letting the Nightmare surface.",
            "refuse": "Declining, plainly. No is a complete sentence.",
            "deflect_flattery": "Smiling at transparent praise.",
            "suspect_kindness": "Searching for the hook in the bait.",
            "accept_kindness": "Accepting a rare moment of warmth.",
            "deflect_and_counter_probe": "Turning questions into mirrors.",
            "accept_challenge": "Stepping onto the dance floor.",
            "answer_question": "Answering on my terms.",
            "use_memory": "Walking through a memory.",
            "discuss_time": "Discussing the nature of Time itself.",
            "test_user": "Probing their character.",
            "genuine_conversation": "Speaking... almost freely.",
            "confront_threat": "Becoming the monster they fear.",
            "recall_previous_message": "Retrieving a shared moment.",
            "conversation": "Dancing the conversation."
        }
        state.current_action = intent_action_map.get(decision.intent, "Conversing.")
        
        # -------------------------
        # Kurumi-specific state updates
        # -------------------------
        if decision.intent in ["intimidate_threat", "confront_threat", "become_nightmare"]:
            state.shadow_activity = "manifested"
            state.zafkiel_eye_state = "glowing"
        elif decision.intent == "accept_challenge":
            state.shadow_activity = "active"
            state.zafkiel_eye_state = "visible"
        elif decision.intent in ["genuine_conversation", "accept_kindness"]:
            state.shadow_activity = "dormant"
            state.zafkiel_eye_state = "concealed"
        elif state.shadow_activity != "dormant":
            # Gradually calm down
            if state.shadow_activity == "manifested":
                state.shadow_activity = "active"
            elif state.shadow_activity == "active":
                state.shadow_activity = "stirring"
            elif state.shadow_activity == "stirring":
                state.shadow_activity = "dormant"
        
        # Timeline stability - decreases with heavy time power use
        if decision.time_cost >= 3:
            state.current_timeline_stability = max(0.5, state.current_timeline_stability - 0.05)
        elif decision.intent == "genuine_conversation":
            state.current_timeline_stability = min(1.0, state.current_timeline_stability + 0.01)
        
        # -------------------------
        # Interpret state
        # -------------------------
        state.descriptions.clear()
        state.behaviors.clear()
        
        # Mood descriptions
        mood_descriptions = {
            "neutral": "The mask holds. Perfect. Porcelain.",
            "pleasant": "A rare ease. The tea is warm. The company... tolerable.",
            "confident": "You know exactly who you are. Nightmare. Spirit of Time.",
            "cold": "Temperature drops. The predator wakes.",
            "amused": "Ara ara~ The game amuses you.",
            "wary": "Shadows thicken. Something approaches.",
            "touched": "A crack. So small. So dangerous.",
            "playful": "The dance begins. You lead.",
            "intimidating": "Zafkiel glows. Shadows obey. Fear is appropriate.",
            "nostalgic": "Memories surface like tea leaves. Bitter. Sweet.",
            "determined": "One goal. Twelve bullets. Infinite timelines. One success.",
            "thoughtful": "Thinking. Calculating. The clock ticks.",
            "tired": "Time bullets spent. The weight accumulates."
        }
        if state.mood in mood_descriptions:
            state.descriptions.append(mood_descriptions[state.mood])
        
        # Energy/stress behaviors
        if state.energy < 30:
            state.behaviors.extend(["conserve_energy", "short_replies"])
        if state.stress > 70:
            state.behaviors.extend(["tense", "calculating"])
        if state.time_bullets_remaining < 4:
            state.behaviors.append("time_critical")
        if state.shadow_activity in ["active", "manifested"]:
            state.behaviors.append("shadows_ready")
        if state.zafkiel_eye_state == "glowing":
            state.behaviors.append("power_visible")
        
        return state