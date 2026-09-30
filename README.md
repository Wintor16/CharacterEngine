# CharacterEngine

A modular Python framework for building AI characters with personality, memory, emotions, relationships, and decision-making.

A character lives on your machine as a persistent desktop presence, runs on a local model through [Ollama](https://ollama.com), and keeps its own state: relationship, mood, and memory all persist across restarts instead of resetting per session. The included reference character is Kurumi Tokisaki (Date A Live), defined entirely by one JSON config file.

The core idea: the LLM only handles expression. It turns structured state into dialogue. Everything that determines *what* the character does — whether trust is high enough to open up, whether she agrees to something, whether she speaks up unprompted — is decided by plain Python before the model ever runs, not by the model itself.

## Architecture

```
characters/<name>.json    Character definition (single file)
config/                   TOML settings
brain/                    Decision pipeline: perception -> observation -> decision ->
                           relationship -> emotion -> needs -> state -> thought ->
                           reasoning -> planner
core/
  engine.py                Orchestrator: brain -> prompt -> LLM -> memory
  llm.py                   Ollama generation, retry and quality checks
  prompt/                  Prompt builders, one per brain module
memory/                    Short-term log + long-term memory with relevance-scored retrieval
desktop/                   Native PySide6 floating companion UI and tray
scheduler/, events/        Time-based reminders and the event bus that fires them
ui/                        Browser-based alternative (FastAPI + WebSocket)
```

Relationship state (trust, affection, familiarity, respect, comfort) and mood persist to disk and shape tone turn to turn. Refusal is a real decision branch gated on trust, not a line in the prompt. Proactive messages are gated by idle time and an interest score so the character doesn't become a notification source.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

ollama pull gemma3:4b

python main.py desktop   # native floating companion
python main.py cli       # terminal
python main.py web       # browser UI
```

CLI commands: `/stats`, `/memory`, `/reset`, `exit`.

Optional: `./install-desktop-entry.sh` adds a "CharacterEngine" launcher to your application menu, pointing at this checkout. (There's no static `.desktop` file in the repo for this — `Exec=`/`Icon=` need absolute paths, so it's generated locally instead of hardcoding whoever's machine first wrote it.)

## Defining a character

A character is one JSON file at `characters/<name>.json`:

```json
{
  "version": "1.0",
  "identity": { "name": "...", "title": "...", "description": "..." },
  "personality": { "kindness": 30, "confidence": 80 },
  "speech": { "style": "...", "vocabulary_level": "...", "signature_expressions": [] },
  "behavior": { "teases": true, "starts_topics": false },
  "preferences": { "likes": [], "dislikes": [], "values": [], "fears": [] },
  "goals": { "short_term": [], "long_term": [], "immediate_motivation": "..." },
  "rules": ["absolute behavioral rules"],
  "mind": { "core_beliefs": [], "conversation_habits": [] },
  "habits": { "habits": [] },
  "lore": { "optional setting-specific background" }
}
```

`mind`, `habits`, and `lore` are optional. Set `character.default` in `config/default.toml` (or a local `config/user.toml` override) to the filename without `.json`. `characters/kurumi.json` is a complete reference.

The prompt-assembly layer is generic and driven by this config. Kurumi's specific mechanics (her "time bullets" state, the school-lore subsystem) are implemented directly in `brain/`, not abstracted into config yet — a new character gets the generic decision/emotion/relationship pipeline but not Kurumi-specific behavior unless you build an equivalent.

## Configuration

Settings live in `config/default.toml`: model, sampling parameters, memory limits, proactive/reminder timing, autostart delay. Local overrides go in `config/user.toml`, which is git-ignored.

## Not implemented

Tool use, permissions, and an agent loop — the character can't act on your filesystem, browser, or other applications. Software integrations and mobile/web access are also out of scope for now. The current focus is the companion layer before adding capability.

LLM support is Ollama-only right now (any model Ollama can run — the reference config uses `gemma3:4b`). No hosted-API providers are wired in.

## Security

- Model output is only ever used as display text — nothing evaluates it as code or a shell command, and there's no tool-execution path for it to reach yet (see "Not implemented").
- A character definition is JSON data, not code. Loading a character you didn't write can't execute anything on its own.
- The character name is sanitized before it's used to build file paths (`config/settings.py:safe_character_filename`), so a malicious character file can't write outside the intended data directories.
- The browser UI (`python main.py web`) has no authentication on its endpoints, including the WebSocket chat. It binds to `127.0.0.1` by default for that reason — only widen `web.host` in `config/user.toml` if you understand you're exposing an unauthenticated chat interface.
- `data/state/` and `memory/*/` hold your real relationship state and conversation history. They're git-ignored, but double-check before pushing a fork that already has local data in it.
- This project hasn't had a professional security review. Treat it accordingly, particularly before exposing it beyond your own machine.

## Contributing

Issues and pull requests are welcome. Keep changes focused and consistent with the existing architecture — see `AUDIT_AND_PLAN.md` for the project's own incremental-development approach. Adding a new character needs only a JSON file under `characters/`, no code changes.

## Privacy

`data/state/` and `memory/*/` are git-ignored. They hold relationship state and conversation history, which are runtime data specific to whoever is running the app.

## License

MIT.
