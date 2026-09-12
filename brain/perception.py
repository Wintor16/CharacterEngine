from dataclasses import dataclass
from typing import List
import re


@dataclass
class PerceptionResult:
    message: str
    normalized_message: str
    message_length: int
    is_question: bool
    is_empty: bool
    is_greeting: bool
    detected_emotion: str = "neutral"
    detected_intent: str = "chat"
    # Kurumi-specific perceptions
    mentions_time: bool = False
    mentions_shido: bool = False
    mentions_westcott: bool = False
    mentions_dem: bool = False
    mentions_spirits: bool = False
    is_threatening: bool = False
    is_flattering: bool = False
    is_genuinely_kind: bool = False
    is_probing_secrets: bool = False
    is_challenging: bool = False
    emotional_tone: str = "neutral"  # neutral, warm, cold, hostile, playful, desperate
    complexity_level: str = "simple"  # simple, moderate, complex, philosophical


class Perception:
    GREETINGS = {
        "hi", "hello", "hey", "good morning", "good afternoon", 
        "good evening", "greetings", "salutations"
    }
    
    # Kurumi-specific keyword detection
    TIME_KEYWORDS = {"time", "clock", "hour", "minute", "second", "eternity", "moment", "timeline", "past", "future", "present", "temporal", "chrono"}
    SHIDO_KEYWORDS = {"shido", "itsuka", "that man", "him", "the boy"}
    WESTCOTT_KEYWORDS = {"westcott", "isaac", "dem", "deus ex machina", "industries", "that man in the suit"}
    SPIRIT_KEYWORDS = {"spirit", "sephira", "astral dress", "angel", "inverse", "tenguu", "spacequake", "kotori", "tohka", "origami", "yoshino", "miku", "natsumi", "yoshinon"}
    THREAT_KEYWORDS = {"kill", "destroy", "eliminate", "hunt", "capture", "stop you", "end you", "monster", "demon", "abomination"}
    FLATTERY_KEYWORDS = {"beautiful", "gorgeous", "stunning", "perfect", "angel", "goddess", "love you", "adore", "worship"}
    KINDNESS_KEYWORDS = {"care", "worry", "help", "support", "understand", "listen", "here for you", "not alone", "friend"}
    PROBING_KEYWORDS = {"why", "how", "what are you", "who are you really", "secret", "truth", "hide", "real reason", "motive", "plan"}
    CHALLENGE_KEYWORDS = {"bet", "challenge", "prove", "dare", "fight", "duel", "test", "show me", "can you"}

    def analyze(self, user_message: str) -> PerceptionResult:
        text = user_message.strip()
        normalized = text.lower()
        
        # Basic detection
        detected_emotion = "neutral"
        if "!" in text:
            detected_emotion = "excited"
        elif text.endswith("..."):
            detected_emotion = "hesitant"
        elif "?" in text and "!" in text:
            detected_emotion = "eager"
        
        is_greeting = any(normalized.startswith(greeting) for greeting in self.GREETINGS)
        
        # Kurumi-specific detections
        mentions_time = any(kw in normalized for kw in self.TIME_KEYWORDS)
        mentions_shido = any(kw in normalized for kw in self.SHIDO_KEYWORDS)
        mentions_westcott = any(kw in normalized for kw in self.WESTCOTT_KEYWORDS)
        mentions_dem = "dem" in normalized or "deus ex machina" in normalized
        mentions_spirits = any(kw in normalized for kw in self.SPIRIT_KEYWORDS)
        is_threatening = any(kw in normalized for kw in self.THREAT_KEYWORDS)
        is_flattering = any(kw in normalized for kw in self.FLATTERY_KEYWORDS)
        is_genuinely_kind = any(kw in normalized for kw in self.KINDNESS_KEYWORDS)
        is_probing_secrets = any(kw in normalized for kw in self.PROBING_KEYWORDS)
        is_challenging = any(kw in normalized for kw in self.CHALLENGE_KEYWORDS)
        
        # Determine emotional tone
        emotional_tone = "neutral"  # Default
        if is_threatening:
            emotional_tone = "hostile"
        elif is_flattering:
            emotional_tone = "playful"  # Kurumi sees through flattery
        elif is_genuinely_kind:
            emotional_tone = "warm"
        elif is_probing_secrets:
            emotional_tone = "cold"
        elif is_challenging:
            emotional_tone = "playful"
        elif mentions_shido:
            emotional_tone = "complex"  # Special tone for Shido mentions
        elif detected_emotion == "excited":
            emotional_tone = "playful"
        elif detected_emotion == "hesitant":
            emotional_tone = "cautious"
        
        # Complexity level
        word_count = len(text.split())
        if word_count > 50 or is_probing_secrets or mentions_shido:
            complexity_level = "philosophical"
        elif word_count > 20 or mentions_time or mentions_spirits:
            complexity_level = "complex"
        elif word_count > 10:
            complexity_level = "moderate"
        else:
            complexity_level = "simple"
        
        # Determine intent
        if is_greeting:
            detected_intent = "greeting"
        elif text.endswith("?"):
            detected_intent = "question"
        elif is_threatening:
            detected_intent = "threat"
        elif is_challenging:
            detected_intent = "challenge"
        elif is_probing_secrets:
            detected_intent = "probe"
        elif is_genuinely_kind:
            detected_intent = "kindness"
        else:
            detected_intent = "chat"
        
        return PerceptionResult(
            message=text,
            normalized_message=normalized,
            message_length=len(text),
            is_question=text.endswith("?"),
            is_empty=len(text) == 0,
            is_greeting=is_greeting,
            detected_emotion=detected_emotion,
            detected_intent=detected_intent,
            mentions_time=mentions_time,
            mentions_shido=mentions_shido,
            mentions_westcott=mentions_westcott,
            mentions_dem=mentions_dem,
            mentions_spirits=mentions_spirits,
            is_threatening=is_threatening,
            is_flattering=is_flattering,
            is_genuinely_kind=is_genuinely_kind,
            is_probing_secrets=is_probing_secrets,
            is_challenging=is_challenging,
            emotional_tone=emotional_tone,
            complexity_level=complexity_level
        )