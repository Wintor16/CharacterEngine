# Kurumi Tokisaki AI - Spirit of Time

An immersive AI chatbot embodying **Kurumi Tokisaki** from *Date A Live*, built with **Gemma 3:4b** via Ollama.

## Features

### 🎭 Deep Character Authenticity
- **Complete Date A Live canon integration**: Zafkiel, 12 Time Bullets (Aleph through Yud Bet), Astral Dress Elohim Gibor, shadow manipulation, clone creation (Het), time acceleration/rewind/freeze
- **Signature mannerisms**: "Ara ara~", elegant archaic speech, clock eye references, shadow imagery, time metaphors
- **Psychological depth**: Complex relationship with Shido Itsuka, hatred for Westcott/DEM, ruthless pragmatism masked by elegance, genuine loneliness beneath the Nightmare persona

### 🧠 Advanced Cognitive Architecture
- **Multi-system Brain**: Perception → Observation → Decision → Relationship → Emotion → Needs → State → Thoughts → Reasoning → Planning
- **Layered Emotions**: Primary/secondary emotions with mask levels (what she shows vs. what she feels)
- **Dynamic Trust System**: 5 trust tiers (Stranger → Acquaintance → Known → Trusted → Inner Circle) affecting behavior
- **Kurumi-Specific Drives**: Time Pressure, Shido Proximity, Secrecy Need, Control Need
- **Inner Monologue & Reflection**: Real-time internal thoughts, end-of-conversation reflections

### 💾 Memory System
- **Short-term**: Conversation history (configurable limit)
- **Long-term**: Automatic memory consolidation from conversations with emotional tagging
- **Memory Categories**: Personal revelations, emotional moments, Kurumi-specific lore, conflicts, intimacy
- **Importance Decay**: Memories weighted by significance, emotional intensity, relationship state

### 🌐 Dual Interface
- **CLI Mode**: Full-featured terminal chat with stats (`/stats`), memory view (`/memory`), reset (`/reset`)
- **Web UI**: Beautiful dark-themed interface with animated clock backgrounds, shadow particles, mood indicators, WebSocket real-time chat

## Quick Start

### Prerequisites
- Python 3.10+
- Ollama installed with `gemma3:4b` model
- Virtual environment recommended

### Installation
```bash
# Create virtual environment
python3 -m venv kurumi_venv
source kurumi_venv/bin/activate

# Install dependencies
pip install ollama fastapi uvicorn jinja2

# Run CLI
python main.py cli

# Or run Web Server
python main.py web
# Access at http://localhost:8000
```

### Usage

**CLI Commands:**
- `exit` / `quit` / `bye` - End conversation
- `/stats` - Show Kurumi's current state (mood, energy, trust, time bullets, etc.)
- `/memory` - View long-term memories
- `/reset` - Clear short-term conversation memory

**Web UI:**
- Real-time chat with thinking indicator
- Mood badges on each response
- Animated background with clock faces and shadow particles
- System messages for connection status

## Architecture

```
characters/kurumi/          # Character definition (JSON files)
├── identity.json           # Core identity, lore, titles
├── personality.json        # 12 personality traits (0-100)
├── speech.json             # Speech patterns, signatures, expressions
├── behavior.json           # Behavioral flags
├── preferences.json        # Likes, dislikes, values, fears
├── goals.json              # Short/long term goals, motivation
├── rules.json              # Absolute character rules
├── habits.json             # Characteristic & combat habits
├── mind.json               # Core beliefs, triggers, conflicts

brain/                      # Cognitive systems
├── perception.py           # Input analysis with Kurumi-specific detection
├── observation.py          # Situation assessment + insights
├── decision.py             # Action selection (15+ intent types)
├── emotion.py              # Layered emotions with mask levels
├── reasoning.py            # Objective-driven chain of thought
├── thought.py              # Priority-ranked internal thoughts
├── planner.py              # Dialogue plan with style flags
├── needs.py                # Kurumi-specific drives (Time Pressure, etc.)
├── relationship.py         # Trust/Familiarity/Affection dynamics
├── state.py                # Full internal state simulation
├── state_updater.py        # State transitions
└── brain.py                # Orchestrator

core/
├── engine.py               # Main pipeline + memory consolidation
├── llm.py                  # Gemma 3:4b optimized generation
└── prompt/                 # Prompt builders for each brain module

memory/
├── manager.py              # Short + long term memory
├── storage.py              # JSON persistence
├── consolidation.py        # Auto memory formation + reflection

ui/
├── app.py                  # FastAPI + WebSocket server
└── templates/index.html    # Dark themed Kurumi UI
```

## Character Voice Examples

> **User:** "Who are you?"
> **Kurumi:** *A slow smile. The clock in her left eye ticks once.* "Ara ara~ Such a direct question. I'm simply a traveler... passing through time. And you? What brings you to this particular moment?"

> **User:** "I like you."
> **Kurumi:** *Her head tilts. Shadows shift at her feet.* "How... troublesome. Affection is a weakness, you know. A liability. But... *her voice softens almost imperceptibly* ...not an unwelcome one. Tell me... what exactly do you see?"

> **User:** "I'll stop you."
> **Kurumi:** *The air pressure drops. Her eye glows gold. Shadows rise like living things.* "Ara... A declaration of war? How thrilling. Very well... *her finger rests on an invisible trigger* ...show me your resolve. But know this: I have burned through ten thousand timelines. You are merely the latest obstacle. Tick tock."

## Configuration

Edit `config.py`:
```python
MODEL = "gemma3:4b"
TEMPERATURE = 0.85
MAX_SHORT_MEMORY = 8
```

LLM parameters in `core/llm.py` optimized for Gemma 3:
- Temperature: 0.85, Top-p: 0.92, Top-k: 40
- Repeat penalty: 1.15, Mirostat 2.0 enabled
- Context: 4096, Max tokens: 300

## Project Structure

```
kurumiai-deneme/
├── main.py                 # Entry point (CLI/Web)
├── config.py               # Model config
├── requirements.txt
├── characters/kurumi/      # Character JSON definitions
├── brain/                  # Cognitive architecture
├── core/                   # Engine, LLM, Prompts
├── memory/                 # Memory systems
├── ui/                     # Web interface
└── README.md
```

## License

MIT License - For educational and creative purposes.

---

*"Time is the only currency that matters. Every second counts. Ara ara~ Shall we begin?"* — Kurumi Tokisaki