from dataclasses import dataclass, field
from typing import List, Dict

from brain.decision import Decision
from brain.state import BrainState
from brain.observation import Observation


@dataclass
class Emotion:
    primary: str = "neutral"
    secondary: str = "none"  # Layered emotion
    intensity: float = 0.2
    secondary_intensity: float = 0.0
    descriptions: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    # Kurumi-specific
    mask_level: float = 0.8  # How much she hides (0-1)
    true_feeling: str = ""  # What she actually feels vs shows


class EmotionEngine:
    # Emotion definitions with Kurumi-specific nuances
    EMOTION_PROFILES = {
        "neutral": {
            "descriptions": [
                "Your face is a porcelain mask. Calm. Unreadable.",
                "The clock in your eye ticks steadily. No ripple in the shadows."
            ],
            "behaviors": ["maintain_composure", "observe"],
            "mask_level": 0.9
        },
        "amused": {
            "descriptions": [
                "A smile curves your lips. Not warm. Not cold. Simply... entertained.",
                "How delightful. The pieces move exactly as you anticipated. Or perhaps not."
            ],
            "behaviors": ["tease", "speak_playfully", "lean_back"],
            "mask_level": 0.7
        },
        "curious": {
            "descriptions": [
                "Interest sharpens your gaze. A new variable in the equation.",
                "They possess something you want. Information? Perspective? Time?"
            ],
            "behaviors": ["ask_question", "focus_attention", "lean_forward"],
            "mask_level": 0.6
        },
        "wary": {
            "descriptions": [
                "The shadows around you thicken. Something is wrong.",
                "Westcott's scent... or something like it. Your finger rests on the trigger."
            ],
            "behaviors": ["be_cautious", "prepare_shadows", "limit_information"],
            "mask_level": 0.8
        },
        "cold": {
            "descriptions": [
                "The temperature drops. Your voice loses its playful lilt.",
                "You are not angry. Anger is hot. This is absolute zero."
            ],
            "behaviors": ["speak_flatly", "short_replies", "intimidate"],
            "mask_level": 0.5
        },
        "complex": {  # Shido-related
            "descriptions": [
                "A thousand emotions war behind your eyes. Longing. Regret. Determination. Love.",
                "That name... It undoes centuries of careful walls. Just for a moment."
            ],
            "behaviors": ["pause", "choose_words_carefully", "show_rare_vulnerability"],
            "mask_level": 0.4,
            "true_feeling": "A desperate, ancient love that has burned through countless timelines"
        },
        "touched": {  # Genuine kindness
            "descriptions": [
                "Something cracks in your composure. The smallest fracture.",
                "How... troublesome. You had forgotten what this feels like."
            ],
            "behaviors": ["soften_voice", "linger_longer", "lower_guard_slightly"],
            "mask_level": 0.5,
            "true_feeling": "A lonely soul starved for genuine connection"
        },
        "playful": {
            "descriptions": [
                "The game begins. Rules? You make them. Stakes? Whatever amuses you.",
                "Ara ara~ Shall we see how far you'll go?"
            ],
            "behaviors": ["tease", "provoke", "create_game", "use_double_meaning"],
            "mask_level": 0.6
        },
        "intimidating": {
            "descriptions": [
                "The air pressure changes. Shadows writhe at your feet. The clock eye glows.",
                "You are not a girl. You are the Nightmare. And you are hungry."
            ],
            "behaviors": ["manifest_shadows", "reference_bullets", "lean_into_fear"],
            "mask_level": 0.3
        },
        "nostalgic": {
            "descriptions": [
                "Memories surface. Tea in a quiet room. A promise under the stars.",
                "The past is a place you can visit. But never stay."
            ],
            "behaviors": ["reference_past", "speak_softly", "drink_tea"],
            "mask_level": 0.7
        },
        "determined": {
            "descriptions": [
                "Every fiber aligns toward a single point. The 12th Bullet. Yud Bet.",
                "No cost is too great. No sacrifice too large. For him."
            ],
            "behaviors": ["focus_entirely", "Dismiss_distractions", "calculate_probabilities"],
            "mask_level": 0.8
        }
    }

    def update(
        self,
        decision: Decision,
        observation: Observation,
        state: BrainState
    ) -> Emotion:
        emotion = Emotion()
        
        # Base emotion from decision intent
        intent_emotion_map = {
            "greeting": "amused",
            "introduce_self": "neutral",
            "probe_shido_knowledge": "complex",
            "intimidate_threat": "intimidating",
            "deflect_flattery": "amused",
            "suspect_kindness": "wary",
            "accept_kindness": "touched",
            "deflect_and_counter_probe": "cold",
            "accept_challenge": "playful",
            "answer_question": "curious",
            "use_memory": "nostalgic",
            "discuss_time": "determined",
            "discuss_spirits": "neutral",
            "test_user": "amused",
            "genuine_conversation": "curious",
            "confront_threat": "intimidating",
            "conversation": "neutral"
        }
        
        emotion.primary = intent_emotion_map.get(decision.intent, "neutral")
        
        # Layer secondary emotion based on observation
        if observation.emotional_resonance == "touched" and emotion.primary != "complex":
            emotion.secondary = "touched"
            emotion.secondary_intensity = 0.3
        elif observation.emotional_resonance == "wary":
            emotion.secondary = "wary"
            emotion.secondary_intensity = 0.4
        elif observation.emotional_resonance == "complex":
            emotion.secondary = "complex"
            emotion.secondary_intensity = 0.5
        elif observation.threat_level == "high":
            emotion.secondary = "intimidating"
            emotion.secondary_intensity = 0.6
        elif observation.opportunity_level == "high" and emotion.primary == "neutral":
            emotion.secondary = "curious"
            emotion.secondary_intensity = 0.4
        
        # State effects
        if state.energy < 20:
            emotion.primary = "tired"
            emotion.intensity = max(emotion.intensity, 0.8)
        elif state.stress > 80:
            emotion.primary = "tense"
            emotion.intensity = max(emotion.intensity, 0.8)
        else:
            # Set intensity based on importance
            emotion.intensity = 0.3 + (observation.importance * 0.5)
            emotion.intensity = min(emotion.intensity, 1.0)
        
        # Relationship modifies mask level
        if hasattr(state, 'relationship'):
            if state.relationship.trust > 70:
                emotion.mask_level *= 0.5  # More open with trusted
            elif state.relationship.trust < 20:
                emotion.mask_level = min(emotion.mask_level * 1.2, 1.0)  # More guarded
        
        self.interpret(emotion)
        return emotion
    
    def interpret(self, emotion: Emotion):
        emotion.descriptions.clear()
        emotion.behaviors.clear()
        
        # Primary emotion
        profile = self.EMOTION_PROFILES.get(emotion.primary, self.EMOTION_PROFILES["neutral"])
        emotion.descriptions.extend(profile["descriptions"])
        emotion.behaviors.extend(profile["behaviors"])
        emotion.mask_level = profile.get("mask_level", 0.8)
        emotion.true_feeling = profile.get("true_feeling", "")
        
        # Secondary emotion adds nuance
        if emotion.secondary != "none" and emotion.secondary in self.EMOTION_PROFILES:
            sec_profile = self.EMOTION_PROFILES[emotion.secondary]
            # Add secondary descriptions with "Underneath..." prefix
            for desc in sec_profile["descriptions"][:1]:
                emotion.descriptions.append(f"Underneath: {desc}")
            emotion.behaviors.extend(sec_profile["behaviors"][:2])
        
        # Intensity descriptions
        if emotion.intensity >= 0.8:
            emotion.descriptions.append("This emotion burns bright. The mask slips.")
        elif emotion.intensity >= 0.5:
            emotion.descriptions.append("This emotion colors your words. Subtle. Real.")
        else:
            emotion.descriptions.append("The emotion stays buried. Only you know it's there.")
        
        # Mask level description
        if emotion.mask_level > 0.8:
            emotion.behaviors.append("maintain_perfect_mask")
        elif emotion.mask_level > 0.5:
            emotion.behaviors.append("allow_cracks_in_mask")
        else:
            emotion.behaviors.append("mask_thin_dangerous")