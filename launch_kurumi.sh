#!/bin/bash
# Kurumi AI - Click to Run (Desktop Entry)

cd "$(dirname "$0")"

# Create virtual environment if not exists
if [ ! -d "kurumi_venv" ]; then
    notify-send "Kurumi AI" "Setting up virtual environment..." 2>/dev/null || echo "Setting up virtual environment..."
    python3 -m venv kurumi_venv
fi

# Install/update dependencies
kurumi_venv/bin/pip install -q ollama fastapi uvicorn jinja2 2>/dev/null

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Check if model exists
if ! kurumi_venv/bin/python -c "import ollama; [m for m in ollama.list()['models'] if 'gemma3:4b' in m['name']]" 2>/dev/null; then
    notify-send "Kurumi AI" "Downloading gemma3:4b model..." 2>/dev/null || echo "Downloading gemma3:4b model..."
    ollama pull gemma3:4b
fi

# Launch web UI in background and open browser
cd "$(dirname "$0")"
kurumi_venv/bin/python main.py web &
SERVER_PID=$!

sleep 2

# Open browser
xdg-open http://localhost:8000 2>/dev/null || open http://localhost:8000 2>/dev/null || sensible-browser http://localhost:8000 2>/dev/null

# Wait for server
wait $SERVER_PID