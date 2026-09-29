#!/bin/bash
# CharacterEngine - Click to Run (Desktop Entry)

cd "$(dirname "$0")"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    notify-send "CharacterEngine" "Setting up virtual environment..." 2>/dev/null || echo "Setting up virtual environment..."
    python3 -m venv venv
fi

# Install/update dependencies
venv/bin/pip install -q ollama fastapi uvicorn jinja2 PySide6 2>/dev/null

# Read the configured model from config/default.toml (single source of
# truth -- see config/settings.py) instead of hardcoding it here too.
MODEL=$(venv/bin/python -c "import tomllib; print(tomllib.load(open('config/default.toml','rb'))['llm']['model'])")

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Check if model exists
if ! ollama list | grep -q "$MODEL"; then
    notify-send "CharacterEngine" "Downloading $MODEL model..." 2>/dev/null || echo "Downloading $MODEL model..."
    ollama pull "$MODEL"
fi

# Launch the native desktop companion (floating avatar + tray icon).
cd "$(dirname "$0")"
venv/bin/python main.py desktop
