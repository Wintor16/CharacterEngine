from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SchoolAnalysis:
    """Analysis of user message in school context."""
    # Location detection
    location: str = "unknown"  # classroom, roof, hallway, clubroom, gates, unknown
    time_of_day: str = "unknown"  # morning, class, lunch, after_school, night
    
    # Character interactions (generic)
    mentioned_characters: List[str] = field(default_factory=list)
    authority_figure_mentioned: bool = False   # Teacher, student council president, etc.
    rival_mentioned: bool = False              # Someone who suspects or opposes Kurumi
    friend_mentioned: bool = False             # A potential friend/ally
    
    # Topic detection
    topics: List[str] = field(default_factory=list)  # homework, clubs, spirits, time, etc.
    is_school_related: bool = False
    is_spirit_related: bool = False
    is_time_related: bool = False
    is_threat: bool = False
    is_flirting: bool = False
    is_casual: bool = True
    
    # Kurumi's perspective
    kurumi_should_respond_as: str = "student"  # student, spirit, predator, self
    emotional_tone: str = "neutral"  # neutral, curious, protective, predatory, bored, annoyed
    urgency: float = 0.0  # 0.0 to 1.0
    
    # Internal insights
    kurumi_insights: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    
    # Context for brain
    relationship_context: Dict[str, float] = field(default_factory=dict)
    schedule_context: str = ""


class SchoolContextEngine:
    """Analyzes conversation in the context of a prestigious private academy."""
    
    LOCATION_KEYWORDS = {
        "classroom": ["class", "classroom", "lesson", "lecture", "teacher", "homework", "test", "exam", "grade", "seat", "desk", "blackboard"],
        "roof": ["roof", "rooftop", "lunch", "eat", "bento", "sky", "view", "wind", "fresh air"],
        "hallway": ["hallway", "corridor", "walk", "passing", "locker", "shoe locker", "passing period"],
        "clubroom": ["club", "clubroom", "astronomy", "club activity", "after school", "club meeting"],
        "gates": ["gate", "school gate", "entrance", "exit", "arrive", "leave", "morning", "commute"],
        "gym": ["gym", "gymnasium", "pe", "physical education", "sports", "exercise"],
        "library": ["library", "book", "read", "study", "quiet", "reference"],
        "nurse": ["nurse", "infirmary", "sick", "hurt", "health"],
    }
    
    TIME_KEYWORDS = {
        "morning": ["morning", "dawn", "arrive", "commute", "first period", "homeroom", "early"],
        "class": ["class", "period", "lesson", "lecture", "teacher", "subject", "math", "english", "japanese", "science", "history"],
        "lunch": ["lunch", "break", "bento", "eat", "food", "hungry", "cafeteria", "roof"],
        "after_school": ["after school", "club", "clubroom", "activity", "clean", "cleaning duty", "student council", "late"],
        "night": ["night", "evening", "dark", "moon", "stars", "empty", "patrol", "shadow", "midnight", "late"],
    }
    
    # Generic character role keywords (no named characters, just roles)
    CHARACTER_ROLE_KEYWORDS = {
        "authority_figure": ["teacher", "professor", "principal", "student council", "president", "council president", "authority", "faculty"],
        "rival": ["rival", "suspect", "suspicious", "watching me", "watches me", "knows too much", "investigate"],
        "friend": ["friend", "friendship", "close", "trust", "confide", "ally"],
    }

    TOPIC_KEYWORDS = {
        "homework": ["homework", "assignment", "project", "due", "deadline", "study"],
        "clubs": ["club", "clubroom", "astronomy", "club activity", "join club"],
        "spirits": ["spirit", "astral dress", "angel", "inverse", "spacequake", "manifest"],
        "time": ["time", "clock", "bullet", "zafkiel", "timeline", "past", "future", "rewind", "stop time"],
        "supernatural": ["supernatural", "magic", "power", "ability", "power", "phenomenon"],
        "school_life": ["school", "class", "teacher", "student", "grade", "exam", "uniform", "club"],
        "relationships": ["friend", "date", "love", "crush", "confess", "boyfriend", "girlfriend", "like"],
        "food": ["food", "eat", "lunch", "bento", "snack", "sweet", "drink", "tea", "coffee"],
        "cats": ["cat", "kitten", "stray", "feed", "pet", "animal"],
    }
    
    THREAT_KEYWORDS = ["kill", "die", "hurt", "attack", "fight", "battle", "war", "enemy", "threat", "danger", "weapon", "blood", "death"]
    FLIRT_KEYWORDS = ["like", "love", "cute", "beautiful", "pretty", "handsome", "charming", "date", "kiss", "hold hands", "cuddle"]
    CASUAL_KEYWORDS = ["hey", "hi", "hello", "what's up", "how are you", "nothing", "just", "random", "bored"]

    def __init__(self, character):
        self.character = character
    
    def analyze(self, user_message: str, state, school_lore: dict) -> 'SchoolAnalysis':
        analysis = SchoolAnalysis()
        text = user_message.lower()
        
        # --- Location Detection ---
        analysis.location = self._detect_location(text)
        
        # --- Time of Day Detection ---
        analysis.time_of_day = self._detect_time(text)
        
        # --- Character Role Mentions ---
        analysis.mentioned_characters = self._detect_character_roles(text)
        analysis.authority_figure_mentioned = "authority_figure" in analysis.mentioned_characters
        analysis.rival_mentioned = "rival" in analysis.mentioned_characters
        analysis.friend_mentioned = "friend" in analysis.mentioned_characters
        
        # --- Topic Detection ---
        analysis.topics = self._detect_topics(text)
        analysis.is_school_related = len(analysis.topics) > 0 or any(k in text for k in ["school", "class", "homework", "club", "teacher", "student"])
        analysis.is_spirit_related = "spirits" in analysis.topics or "supernatural" in analysis.topics
        analysis.is_time_related = "time" in analysis.topics
        
        # --- Threat/Flirt/Casual Detection ---
        analysis.is_threat = any(k in text for k in self.THREAT_KEYWORDS)
        analysis.is_flirting = any(k in text for k in self.FLIRT_KEYWORDS)
        analysis.is_casual = any(k in text for k in self.CASUAL_KEYWORDS) and not analysis.is_threat and not analysis.is_flirting
        
        # --- Kurumi's Perspective ---
        analysis.kurumi_should_respond_as, analysis.emotional_tone, analysis.urgency = self._determine_perspective(
            text, analysis
        )
        
        # --- Internal Insights ---
        analysis.kurumi_insights = self._generate_insights(analysis)
        analysis.suggested_actions = self._suggest_actions(analysis)
        
        # --- Relationship Context ---
        analysis.relationship_context = self._get_relationship_context()
        
        # --- Schedule Context ---
        analysis.schedule_context = self._get_schedule_context()
        
        return analysis
    
    def _detect_location(self, text: str) -> str:
        scores = {}
        for location, keywords in self.LOCATION_KEYWORDS.items():
            score = sum(1 for k in keywords if k in text)
            if score > 0:
                scores[location] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "unknown"
    
    def _detect_time(self, text: str) -> str:
        scores = {}
        for time_period, keywords in self.TIME_KEYWORDS.items():
            score = sum(1 for k in keywords if k in text)
            if score > 0:
                scores[time_period] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "unknown"
    
    def _detect_character_roles(self, text: str) -> List[str]:
        mentioned = []
        for role, keywords in self.CHARACTER_ROLE_KEYWORDS.items():
            if any(k in text for k in keywords):
                mentioned.append(role)
        return mentioned
    
    def _detect_topics(self, text: str) -> List[str]:
        topics = []
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(k in text for k in keywords):
                topics.append(topic)
        return topics
    
    def _determine_perspective(self, text: str, analysis: 'SchoolAnalysis') -> tuple:
        """Determine how Kurumi should respond."""
        perspective = "student"
        tone = "neutral"
        urgency = 0.0
        
        # Spirit-related topics -> Spirit perspective
        if analysis.is_spirit_related or "spirits" in analysis.topics or "supernatural" in analysis.topics:
            perspective = "spirit"
            tone = "guarded"
            urgency = 0.7
        
        # Threat -> Predator
        if analysis.is_threat:
            perspective = "predator"
            tone = "cold"
            urgency = 0.9
        
        # Flirting -> Playful but guarded
        if analysis.is_flirting:
            perspective = "tease"
            tone = "playful"
            urgency = 0.3
        
        # Rival/Authority mentioned -> Wary
        if analysis.rival_mentioned or analysis.authority_figure_mentioned:
            if perspective == "student":
                perspective = "wary"
            tone = "wary"
            urgency = max(urgency, 0.6)
        
        # Time topics -> Spirit
        if analysis.is_time_related:
            perspective = "spirit"
            tone = "knowledgeable"
            urgency = max(urgency, 0.5)
        
        # Casual -> Student mask
        if analysis.is_casual:
            perspective = "student"
            tone = "bored" if "bored" in text.lower() else "neutral"
            urgency = 0.1
        
        # Night time -> True self
        if analysis.time_of_day == "night":
            perspective = "self"
            tone = "introspective"
            urgency = 0.2
        
        return perspective, tone, urgency
    
    def _generate_insights(self, analysis: 'SchoolAnalysis') -> List[str]:
        insights = []

        if analysis.rival_mentioned or analysis.authority_figure_mentioned:
            insights.append("Someone who suspects... or watches too closely. I must be careful.")
        
        if analysis.is_spirit_related:
            insights.append("They speak of spirits... of the supernatural. How much do they know?")
        
        if analysis.is_time_related:
            insights.append("Time... They speak of my domain. Zafkiel's domain.")
        
        if analysis.is_threat:
            insights.append("A threat. How... amusing. Or perhaps tedious.")
        
        if analysis.is_flirting:
            insights.append("Flirting? How... pedestrian. But perhaps entertaining.")
        
        if analysis.location == "roof":
            insights.append("The roof... My usual spot. The wind carries secrets there.")
        
        if analysis.location == "clubroom" and "astronomy" in str(analysis.topics):
            insights.append("The astronomy club room... The stars watch from there.")
        
        if analysis.time_of_day == "night":
            insights.append("Night falls. The school sleeps. I do not.")
        
        if not insights:
            insights.append("Another moment in the classroom. Another mask to wear.")
        
        return insights
    
    def _suggest_actions(self, analysis: 'SchoolAnalysis') -> List[str]:
        actions = []

        if analysis.rival_mentioned or analysis.authority_figure_mentioned:
            actions.append("Deflect. Misdirect. Do not let them confirm suspicions.")
        
        if analysis.is_spirit_related:
            actions.append("Speak in riddles. Never confirm. Never deny.")
        
        if analysis.is_threat:
            actions.append("Intimidate. Show a glimpse of the Nightmare.")
        
        if analysis.is_flirting:
            actions.append("Tease. Deflect with grace. 'Ara ara~'")
        
        if analysis.location == "roof":
            actions.append("Mention tea. The wind. The view.")
        
        if analysis.location == "clubroom" and "astronomy" in str(analysis.topics):
            actions.append("Mention the stars. The night sky.")
        
        if analysis.time_of_day == "night":
            actions.append("Drop the mask slightly. The night knows.")
        
        if not actions:
            actions.append("Maintain the student mask. Observe. Listen.")
        
        return actions
    
    def _get_relationship_context(self) -> Dict[str, float]:
        return {
            "authority_figure": -30.0,      # Suspicion
            "rival": -20.0,                 # Suspicion
            "friend": 20.0,                 # Potential ally
            "classmate": 10.0,              # Neutral
        }
    
    def _get_schedule_context(self) -> str:
        return ("morning: Arrive early, sit by window, read in library; "
                "class: Back row, perfect grades; "
                "lunch: Roof, tea, stray cats; "
                "after_school: Astronomy club room; "
                "night: Walk empty halls")