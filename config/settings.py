"""Central configuration for CharacterEngine.

Resolves PROJECT_ROOT once from this file's own location, so every path
in the app is anchored regardless of the process's working directory --
important for autostart/systemd launches, which don't run from the
project directory. Loads config/default.toml, merged with an optional
config/user.toml (git-ignored) for local overrides.
"""

import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"

CHARACTERS_DIR = PROJECT_ROOT / "characters"
MEMORY_DIR = PROJECT_ROOT / "memory"
DATA_DIR = PROJECT_ROOT / "data"


def _load_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


_settings = _merge(
    _load_toml(CONFIG_DIR / "default.toml"),
    _load_toml(CONFIG_DIR / "user.toml"),
)


def get(*keys, default=None):
    """Dotted lookup into the merged settings, e.g. get('llm', 'model')."""
    node = _settings
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


DEFAULT_CHARACTER = get("character", "default", default="kurumi")

MODEL = get("llm", "model", default="gemma3:4b")
TEMPERATURE = get("llm", "temperature", default=0.85)
TOP_P = get("llm", "top_p", default=0.92)
TOP_K = get("llm", "top_k", default=40)
REPEAT_PENALTY = get("llm", "repeat_penalty", default=1.15)
NUM_PREDICT = get("llm", "num_predict", default=300)
NUM_CTX = get("llm", "num_ctx", default=8192)

WEB_HOST = get("web", "host", default="0.0.0.0")
WEB_PORT = get("web", "port", default=8000)

HISTORY_LIMIT = get("memory", "history_limit", default=8)
SHORT_TERM_LIMIT = get("memory", "short_term_limit", default=20)
LONG_TERM_LIMIT = get("memory", "long_term_limit", default=1000)

AUTOSTART_DELAY_SECONDS = get("autostart", "delay_seconds", default=10)

PROACTIVE_ENABLED = get("proactive", "enabled", default=True)
PROACTIVE_CHECK_INTERVAL_MINUTES = get("proactive", "check_interval_minutes", default=5)
PROACTIVE_MIN_IDLE_MINUTES = get("proactive", "min_idle_minutes", default=20)
PROACTIVE_MIN_GAP_MINUTES = get("proactive", "min_gap_minutes", default=30)

SCHEDULER_CHECK_INTERVAL_SECONDS = get("scheduler", "check_interval_seconds", default=30)
