#!/bin/bash
# Kurumi AI Launcher - Click to run

cd "$(dirname "$0")"

echo "Starting Kurumi AI..."

# Check if virtual environment exists
if [ ! -d "kurumi_venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv kurumi_venv
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
kurumi_venv/bin/pip install -q ollama fastapi uvicorn jinja2

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Check if model exists
if ! kurumi_venv/bin/python -c "import ollama; ollama.list()" 2>/dev/null | grep -q "gemma3:4b"; then
    echo "Pulling gemma3:4b model..."
    ollama pull gemma3:4b
fi

echo ""
echo "=========================================="
echo "  Kurumi Tokisaki AI"
echo "  Spirit of Time - Nightmare"
echo "=========================================="
echo ""
echo "Choose mode:"
echo "  1) CLI Chat (terminal)"
echo "  2) Web UI (browser - http://localhost:8000)"
echo "  3) Both"
echo ""
read -p "Enter choice [1/2/3]: " choice

case $choice in
    1)
        echo "Starting CLI mode..."
        kurumi_venv/bin/python main.py cli
        ;;
    2)
        echo "Starting Web UI at http://localhost:8000"
        echo "Press Ctrl+C to stop"
        kurumi_venv/bin/python main.py web
        ;;
    3)
        echo "Starting Web UI in background..."
        kurumi_venv/bin/python main.py web &
        sleep 2
        echo "Starting CLI mode..."
        kurumi_venv/bin/python main.py cli
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac