from dataclasses import dataclass


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
    is_threatening: bool = False
    is_flattering: bool = False
    is_genuinely_kind: bool = False
    is_probing_secrets: bool = False
    is_challenging: bool = False
    is_demanding: bool = False
    emotional_tone: str = "neutral"  # neutral, warm, cold, hostile, playful, desperate
    complexity_level: str = "simple"  # simple, moderate, complex, philosophical


class Perception:
    GREETINGS = {
        "hi", "hello", "hey", "good morning", "good afternoon", 
        "good evening", "greetings", "salutations"
    }
    
    # Kurumi-specific keyword detection
    # "second"/"minute" deliberately excluded -- "for a second", "wait a
    # minute" are common idioms, not actually about time, and were
    # mis-triggering discuss_time for unrelated messages that just
    # happened to contain them (e.g. "just be honest with me for a second").
    TIME_KEYWORDS = {"time", "clock", "hour", "eternity", "moment", "timeline", "past", "future", "present", "temporal", "chrono"}
    THREAT_KEYWORDS = {"kill", "destroy", "eliminate", "hunt", "capture", "stop you", "end you", "monster", "demon", "abomination"}
    FLATTERY_KEYWORDS = {"beautiful", "gorgeous", "stunning", "perfect", "angel", "goddess", "love you", "adore", "worship",
                         "pretty", "cute", "attractive", "lovely", "hot", "sexy", "charming", "amazing", "incredible", "flawless"}
    KINDNESS_KEYWORDS = {"care", "worry", "help", "support", "understand", "listen", "here for you", "not alone", "friend"}
    # Deliberately specific phrases, not bare "why"/"how" -- those match
    # almost any question (including "how are you") and were causing
    # ordinary small talk to be treated as adversarial secret-probing.
    PROBING_KEYWORDS = {"what are you", "who are you really", "your secret", "the truth", "what are you hiding",
                        "real reason", "your motive", "what's your plan", "are you hiding"}
    CHALLENGE_KEYWORDS = {"bet", "challenge", "prove", "dare", "fight", "duel", "i dare you", "show me what"}
    # Being ordered around, not asked -- this is what lets her actually
    # refuse something structurally (see decision.py) instead of "being
    # capable of refusing" only existing as unenforced prompt text.
    DEMAND_KEYWORDS = {"you must", "you have to", "do it now", "i order you", "you will do",
                       "right now, no excuses", "shut up and", "stop arguing and", "obey me"}

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
        is_threatening = any(kw in normalized for kw in self.THREAT_KEYWORDS)
        is_flattering = any(kw in normalized for kw in self.FLATTERY_KEYWORDS)
        is_genuinely_kind = any(kw in normalized for kw in self.KINDNESS_KEYWORDS)
        is_probing_secrets = any(kw in normalized for kw in self.PROBING_KEYWORDS)
        is_challenging = any(kw in normalized for kw in self.CHALLENGE_KEYWORDS)
        is_demanding = any(kw in normalized for kw in self.DEMAND_KEYWORDS)
        
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
        elif detected_emotion == "excited":
            emotional_tone = "playful"
        elif detected_emotion == "hesitant":
            emotional_tone = "cautious"
        
        # Complexity level
        word_count = len(text.split())
        if word_count > 50 or is_probing_secrets:
            complexity_level = "philosophical"
        elif word_count > 20 or mentions_time:
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
            is_threatening=is_threatening,
            is_flattering=is_flattering,
            is_genuinely_kind=is_genuinely_kind,
            is_probing_secrets=is_probing_secrets,
            is_challenging=is_challenging,
            is_demanding=is_demanding,
            emotional_tone=emotional_tone,
            complexity_level=complexity_level
        )