import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import deque
import hashlib

@dataclass
class Memory:
    id: str
    content: str
    memory_type: str  # "episodic", "semantic", "emotional", "procedural"
    importance: float  # 0.0 to 1.0
    timestamp: str
    tags: List[str] = field(default_factory=list)
    emotional_valence: float = 0.0  # -1.0 to 1.0
    related_entities: List[str] = field(default_factory=list)
    context: str = ""
    access_count: int = 0
    last_accessed: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class AdvancedMemorySystem:
    def __init__(self, character_name: str, max_short_term: int = 20, max_long_term: int = 1000):
        self.character_name = character_name
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        
        # Short-term: recent conversation context (working memory)
        self.short_term = deque(maxlen=max_short_term)
        
        # Long-term: consolidated memories
        self.long_term: List[Memory] = []
        
        # Memory index for fast retrieval
        self.entity_index: Dict[str, List[str]] = {}  # entity -> memory_ids
        self.tag_index: Dict[str, List[str]] = {}
        
        # Load existing memories
        self.memory_dir = Path(f"memory/{character_name}")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.load_memories()

    def _generate_id(self, content: str) -> str:
        return hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    def add_short_term(self, role: str, content: str, metadata: Dict = None):
        """Add to working memory (short-term)."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.short_term.append(entry)
    
    def get_short_term(self, limit: int = None) -> List[Dict]:
        """Get recent conversation history."""
        if limit:
            return list(self.short_term)[-limit:]
        return list(self.short_term)
    
    def clear_short_term(self):
        self.short_term.clear()
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text."""
        entities = []
        # Simple entity extraction - can be enhanced with NER
        keywords = ["shido", "itsuka", "origami", "tohka", "kotori", "miku", "natsumi", 
                    "westcott", "dem", "ratatoskr", "zafkiel", "spirit", "astral dress",
                    "time bullet", "yud bet", "aleph", "school", "class", "roof", "classroom"]
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                entities.append(kw)
        return entities
    
    def _analyze_emotion(self, text: str) -> float:
        """Analyze emotional valence of text (-1 to 1)."""
        positive = ["happy", "love", "like", "good", "great", "wonderful", "beautiful", 
                   "happy", "joy", "smile", "laugh", "warm", "kind", "gentle"]
        negative = ["hate", "angry", "sad", "bad", "terrible", "awful", "pain", "hurt",
                   "fear", "scared", "cold", "cruel", "monster", "nightmare", "kill"]
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        
        if pos_count + neg_count == 0:
            return 0.0
        return (pos_count - neg_count) / (pos_count + neg_count)
    
    def _determine_memory_type(self, role: str, content: str, entities: List[str]) -> str:
        """Determine what type of memory this should be."""
        content_lower = content.lower()
        
        if any(w in content_lower for w in ["remember", "recall", "memory", "past", "before"]):
            return "episodic"
        elif any(w in content_lower for w in ["feel", "feeling", "emotion", "love", "hate", "fear", "happy", "sad"]):
            return "emotional"
        elif any(w in content_lower for w in ["how to", "learn", "know", "understand", "fact", "information"]):
            return "semantic"
        elif any(w in content_lower for w in ["do", "action", "did", "will do", "plan"]):
            return "procedural"
        return "episodic"
    
    def add_memory(
        self,
        content: str,
        memory_type: str = "episodic",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        emotional_valence: float = 0.0,
        related_entities: Optional[List[str]] = None,
        context: str = "",
        timestamp: Optional[str] = None,
    ) -> Memory:
        """Single write path for long-term memories. Callers (e.g. MemoryConsolidator)
        decide what is worth remembering; this just persists and indexes it."""
        memory = Memory(
            id=self._generate_id(content),
            content=content,
            memory_type=memory_type,
            importance=importance,
            timestamp=timestamp or datetime.now().isoformat(),
            tags=tags or [],
            emotional_valence=emotional_valence,
            related_entities=related_entities or [],
            context=context,
        )

        self.long_term.append(memory)
        self._index_memory(memory)

        # Trim if over limit
        if len(self.long_term) > self.max_long_term:
            self.long_term.sort(key=lambda m: m.importance * (m.access_count + 1))
            self.long_term = self.long_term[-self.max_long_term:]
            self._rebuild_indices()

        self.save_memories()
        return memory

    def _index_memory(self, memory: Memory):
        """Add memory to indices."""
        for entity in memory.related_entities:
            if entity not in self.entity_index:
                self.entity_index[entity] = []
            self.entity_index[entity].append(memory.id)
        
        for tag in memory.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(memory.id)
    
    def _rebuild_indices(self):
        self.entity_index.clear()
        self.tag_index.clear()
        for mem in self.long_term:
            self._index_memory(mem)
    
    def retrieve(self, query: str, limit: int = 5) -> List[Memory]:
        """Retrieve relevant long-term memories."""
        query_lower = query.lower()
        query_entities = self._extract_entities(query)
        query_tags = query_lower.split()
        
        scored = []
        for mem in self.long_term:
            score = 0.0
            
            # Entity match
            for entity in query_entities:
                if entity in mem.related_entities:
                    score += 0.4
            
            # Tag match
            for tag in query_tags:
                if tag in mem.tags:
                    score += 0.2
            
            # Content similarity (simple keyword overlap)
            query_words = set(query_lower.split())
            mem_words = set(mem.content.lower().split())
            overlap = len(query_words & mem_words)
            score += min(overlap * 0.05, 0.3)
            
            # Recency bonus
            try:
                mem_time = datetime.fromisoformat(mem.timestamp)
                hours_ago = (datetime.now() - mem_time).total_seconds() / 3600
                if hours_ago < 24:
                    score += 0.1
                elif hours_ago < 168:  # week
                    score += 0.05
            except:
                pass
            
            # Importance weight
            score *= mem.importance
            
            if score > 0:
                scored.append((score, mem))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Update access stats
        results = [m for _, m in scored[:limit]]
        for m in results:
            m.access_count += 1
            m.last_accessed = datetime.now().isoformat()
        
        if results:
            self.save_memories()
        
        return results
    
    def get_memories_by_entity(self, entity: str, limit: int = 10) -> List[Memory]:
        """Get all memories related to an entity."""
        ids = self.entity_index.get(entity, [])
        memories = [m for m in self.long_term if m.id in ids]
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        return memories[:limit]
    
    def get_recent_memories(self, hours: int = 24, limit: int = 20) -> List[Memory]:
        """Get recent memories within time window."""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        recent = []
        for mem in self.long_term:
            try:
                mem_time = datetime.fromisoformat(mem.timestamp).timestamp()
                if mem_time >= cutoff:
                    recent.append(mem)
            except:
                pass
        recent.sort(key=lambda m: m.timestamp, reverse=True)
        return recent[:limit]
    
    def save_memories(self):
        """Save long-term memories to disk."""
        filepath = self.memory_dir / "long_term.json"
        data = [m.to_dict() for m in self.long_term]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_memories(self):
        """Load long-term memories from disk."""
        filepath = self.memory_dir / "long_term.json"
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.long_term = [Memory.from_dict(d) for d in data]
            self._rebuild_indices()
        except Exception as e:
            print(f"Failed to load memories: {e}")
            self.long_term = []

    def get_stats(self) -> Dict:
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "entity_count": len(self.entity_index),
            "tag_count": len(self.tag_index),
            "memory_types": {
                t: len([m for m in self.long_term if m.memory_type == t])
                for t in ["episodic", "semantic", "emotional", "procedural"]
            }
        }