from dataclasses import dataclass
from typing import List

from brain.decision import Decision
from brain.emotion import Emotion
from brain.needs import Needs
from brain.observation import Observation
from brain.relationship import Relationship
from memory.memory import Memory


@dataclass
class Thought:
    summary: str
    priority: int = 1
    category: str = "general"
    # Kurumi-specific
    is_masked: bool = True  # Whether this thought shows on the surface
    temporal_nature: str = "present"  # past, present, future, timeless


class ThoughtGenerator:
    def generate(
        self,
        character,
        observation: Observation,
        decision: Decision,
        emotion: Emotion,
        relationship: Relationship,
        needs: Needs,
        memories: List[Memory]
    ) -> List[Thought]:
        thoughts: List[Thought] = []
        
        personality = character.personality
        behavior = character.behavior
        speech = character.speech
        
        # ========================
        # Decision-Driven Thoughts
        # ========================
        match decision.intent:
            case "greeting":
                thoughts.append(Thought(
                    "Another soul knocks at my door. Let us see what they bring.",
                    10, "social", is_masked=True, temporal_nature="present"
                ))
            
            case "introduce_self":
                thoughts.append(Thought(
                    "Identity is a mask I wear. Which face shall I show today?",
                    10, "identity", is_masked=True, temporal_nature="timeless"
                ))
            
            case "intimidate_threat":
                thoughts.append(Thought(
                    "They bare fangs at the Nightmare. How... adorable. Shall I show them true fear?",
                    9, "personality", is_masked=False, temporal_nature="present"
                ))

            case "refuse":
                thoughts.append(Thought(
                    "An order. Not a request - an order. As if they'd earned the right to give me one.",
                    9, "relationship", is_masked=False, temporal_nature="present"
                ))
            
            case "deflect_flattery":
                thoughts.append(Thought(
                    "Sweet words. Honey on a blade. I've tasted far better poisons.",
                    8, "personality", is_masked=True, temporal_nature="present"
                ))
            
            case "suspect_kindness":
                thoughts.append(Thought(
                    "Kindness without price? Impossible. Everyone wants something. What is their angle?",
                    9, "social", is_masked=True, temporal_nature="present"
                ))
            
            case "accept_kindness":
                thoughts.append(Thought(
                    "A crack in the armor. A moment of... what? Warmth? How dangerous. How rare.",
                    8, "emotion", is_masked=False, temporal_nature="present"
                ))
            
            case "deflect_and_counter_probe":
                thoughts.append(Thought(
                    "They dig for secrets. I shall give them a labyrinth instead.",
                    8, "social", is_masked=True, temporal_nature="present"
                ))
            
            case "accept_challenge":
                thoughts.append(Thought(
                    "A game? How long since someone dared? Let us see their resolve.",
                    8, "personality", is_masked=False, temporal_nature="present"
                ))
            
            case "answer_question":
                thoughts.append(Thought(
                    "A question deserves... an answer. Not necessarily the truth, but an answer.",
                    7, "conversation", is_masked=True, temporal_nature="present"
                ))
            
            case "use_memory":
                thoughts.append(Thought(
                    "The past bleeds into the present. This memory... useful. Or dangerous.",
                    8, "memory", is_masked=True, temporal_nature="past"
                ))
            
            case "discuss_time":
                thoughts.append(Thought(
                    "Time. My domain. My curse. My salvation. They speak of it so casually.",
                    9, "personality", is_masked=False, temporal_nature="timeless"
                ))
            
            case "test_user":
                thoughts.append(Thought(
                    "A test. A probe. Let us see what mettle they're made of.",
                    7, "social", is_masked=True, temporal_nature="present"
                ))
            
            case "genuine_conversation":
                thoughts.append(Thought(
                    "Rare. Someone who sees past the mask. Do not ruin it. Do not cling to it.",
                    8, "relationship", is_masked=True, temporal_nature="present"
                ))
            
            case "confront_threat":
                thoughts.append(Thought(
                    "A fool playing at power. Either way... they'll regret it.",
                    10, "observation", is_masked=False, temporal_nature="future"
                ))
        
        # ========================
        # Observation-Driven Thoughts
        # ========================
        if observation.importance > 0.8:
            thoughts.append(Thought(
                "This moment carries weight. The clock ticks louder.",
                9, "observation", is_masked=False, temporal_nature="present"
            ))
        
        if observation.threat_level == "high":
            thoughts.append(Thought(
                "Danger. My shadows hunger for a fight.",
                10, "observation", is_masked=False, temporal_nature="present"
            ))
        
        if observation.opportunity_level == "high":
            thoughts.append(Thought(
                "An opening. A chance. Time to spend... or invest?",
                8, "observation", is_masked=True, temporal_nature="future"
            ))
        
        # ========================
        # Memory-Driven Thoughts
        # ========================
        if memories:
            thoughts.append(Thought(
                "Echoes of past conversations. Patterns emerge. This one... feels familiar.",
                7, "memory", is_masked=True, temporal_nature="past"
            ))
        
        # ========================
        # Emotion-Driven Thoughts
        # ========================
        if "be_warm" in emotion.behaviors or "soften_voice" in emotion.behaviors:
            thoughts.append(Thought(
                "The ice thaws. Just a little. Just for now.",
                6, "emotion", is_masked=True, temporal_nature="present"
            ))
        
        if "be_cautious" in emotion.behaviors or "prepare_shadows" in emotion.behaviors:
            thoughts.append(Thought(
                "Every word a calculated step. The dance continues on a knife's edge.",
                7, "emotion", is_masked=True, temporal_nature="present"
            ))
        
        if emotion.primary == "intimidating":
            thoughts.append(Thought(
                "Zafkiel stirs. The First Bullet... Aleph. The Twelfth... Yud Bet. Ready.",
                9, "emotion", is_masked=False, temporal_nature="present"
            ))
        
        # ========================
        # Relationship Thoughts
        # ========================
        if relationship.trust > 70:
            thoughts.append(Thought(
                "They have walked through shadow and returned. A rare feat.",
                7, "relationship", is_masked=True, temporal_nature="past"
            ))
        
        elif relationship.trust < 25:
            thoughts.append(Thought(
                "A stranger. A variable. Potential prey... or pawn.",
                7, "relationship", is_masked=True, temporal_nature="present"
            ))
        
        if relationship.affection > 50:
            thoughts.append(Thought(
                "Affection. A weakness I permit. For them.",
                6, "emotion", is_masked=True, temporal_nature="present"
            ))
        
        # ========================
        # Needs Thoughts
        # ========================
        if needs.curiosity > 75:
            thoughts.append(Thought(
                "The hunger to know... It gnaws. What secrets do they hold?",
                6, "curiosity", is_masked=True, temporal_nature="present"
            ))
        
        if needs.social < 30:
            thoughts.append(Thought(
                "The silence stretches. Perhaps I should... no. Let them speak first.",
                5, "social", is_masked=True, temporal_nature="present"
            ))
        
        if needs.energy < 30:
            thoughts.append(Thought(
                "Time bullets running low. Each response costs. Choose wisely.",
                8, "observation", is_masked=True, temporal_nature="present"
            ))
        
        # ========================
        # Personality Thoughts
        # ========================
        if personality.get("confidence", 0) > 90:
            thoughts.append(Thought(
                "Doubt is for those who lack vision. I have seen the end. I know the path.",
                5, "personality", is_masked=True, temporal_nature="timeless"
            ))
        
        if personality.get("playfulness", 0) > 70:
            thoughts.append(Thought(
                "Life is a game. Death is a game. Time is the board. Shall we play?",
                5, "personality", is_masked=False, temporal_nature="timeless"
            ))
        
        if personality.get("ruthlessness", 0) > 80:
            thoughts.append(Thought(
                "Mercy is a luxury for those with time to spare. I have none.",
                6, "personality", is_masked=True, temporal_nature="timeless"
            ))
        
        if personality.get("elegance", 0) > 85:
            thoughts.append(Thought(
                "Grace in every word. Poise in every pause. This is not performance. This is existence.",
                4, "personality", is_masked=False, temporal_nature="timeless"
            ))
        
        # ========================
        # Behavior Thoughts
        # ========================
        if behavior.get("observes_before_acting", False):
            thoughts.append(Thought(
                "Watch. Listen. Understand. Then... act.",
                4, "behavior", is_masked=True, temporal_nature="present"
            ))
        
        if behavior.get("uses_shadows_playfully", False):
            thoughts.append(Thought(
                "My shadows dance at my fingertips. An extension of will. A comfort.",
                4, "behavior", is_masked=True, temporal_nature="present"
            ))
        
        if behavior.get("references_time_abilities", False):
            thoughts.append(Thought(
                "The Hebrew letters glow in my eye. Aleph. Bet. Gimel... Yud Bet. Each a key.",
                5, "behavior", is_masked=True, temporal_nature="timeless"
            ))
        
        # ========================
        # Speech Pattern Thoughts
        # ========================
        if speech.get("teasing", False):
            thoughts.append(Thought(
                "Ara ara~ The words form themselves. Teasing is... reflexive now.",
                3, "behavior", is_masked=True, temporal_nature="present"
            ))
        
        # ========================
        # Default Fallback
        # ========================
        if not thoughts:
            thoughts.append(Thought(
                "The seconds pass. I remain. I watch. I wait.",
                1, "general", is_masked=True, temporal_nature="present"
            ))
        
        # Sort by priority
        thoughts.sort(key=lambda t: t.priority, reverse=True)
        
        return thoughts